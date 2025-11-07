from __future__ import annotations

from datetime import datetime, timedelta
from functools import wraps
from typing import Iterable

from django.db.models import F, Prefetch
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import (
    Championship,
    ChampionshipMatch,
    ChampionshipTeam,
    League,
    Season,
)


def _login_required_json(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        return view(request, *args, **kwargs)

    return wrapped


def _season_to_dict(season: Season) -> dict:
    return {
        "id": season.id,
        "name": season.name,
        "number": season.number,
        "is_active": season.is_active,
        "start_date": season.start_date.isoformat(),
        "end_date": season.end_date.isoformat(),
    }


def _league_to_dict(league: League) -> dict:
    country = getattr(league.country, "name", None) or str(league.country)
    return {
        "id": league.id,
        "name": league.name,
        "country": country,
        "level": league.level,
        "max_teams": league.max_teams,
    }


def _championship_to_summary(championship: Championship) -> dict:
    return {
        "id": championship.id,
        "name": str(championship),
        "status": championship.status,
        "start_date": championship.start_date.isoformat(),
        "end_date": championship.end_date.isoformat(),
        "match_time": championship.match_time.isoformat(),
        "season": _season_to_dict(championship.season),
        "league": _league_to_dict(championship.league),
    }


def _team_to_dict(team: ChampionshipTeam) -> dict:
    club = team.team
    crest_url = getattr(club, "crest_url", None)
    short_name = getattr(club, "short_name", None)
    return {
        "id": club.id,
        "name": club.name,
        "short_name": short_name,
        "crest_url": crest_url,
    }


def _standing_to_dict(team: ChampionshipTeam, position: int, total: int) -> dict:
    relegation_cutoff = max(total - 1, 1)
    promotion_cutoff = min(2, total)
    goal_diff = team.goals_for - team.goals_against
    return {
        "team": _team_to_dict(team),
        "position": position,
        "matches_played": team.matches_played,
        "wins": team.wins,
        "draws": team.draws,
        "losses": team.losses,
        "goals_for": team.goals_for,
        "goals_against": team.goals_against,
        "goal_diff": goal_diff,
        "points": team.points,
        "is_relegation_zone": position >= relegation_cutoff,
        "is_promotion_zone": position <= promotion_cutoff,
    }


def _match_date(match: ChampionshipMatch) -> datetime:
    if match.match and match.match.datetime:
        dt = match.match.datetime
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.get_default_timezone())
        return timezone.localtime(dt)

    base_date = match.championship.start_date + timedelta(days=max(match.match_day - 1, 0))
    kickoff_time = match.championship.match_time
    naive_dt = datetime.combine(base_date, kickoff_time)
    if timezone.is_naive(naive_dt):
        return timezone.make_aware(naive_dt, timezone.get_default_timezone())
    return naive_dt


def _match_to_dict(match: ChampionshipMatch) -> dict:
    home = match.match.home_team
    away = match.match.away_team
    score = (
        {"home": match.match.home_score, "away": match.match.away_score}
        if match.match.status == "finished"
        else None
    )
    scheduled_dt = _match_date(match)
    return {
        "id": match.id,
        "round": match.round,
        "match_day": match.match_day,
        "date": scheduled_dt.isoformat(),
        "status": match.match.status,
        "processed": match.processed,
        "match_id": match.match.id,
        "home_team": {
            "id": home.id,
            "name": home.name,
        },
        "away_team": {
            "id": away.id,
            "name": away.name,
        },
        "score": score,
    }


def _championship_with_related() -> Iterable[Championship]:
    return Championship.objects.select_related("season", "league")


@require_GET
@_login_required_json
def season_list(request):
    seasons = Season.objects.all().order_by("-start_date")
    return JsonResponse([_season_to_dict(season) for season in seasons], safe=False)


@require_GET
@_login_required_json
def league_list(request):
    qs = League.objects.all().order_by("country", "level")
    if country := request.GET.get("country"):
        qs = qs.filter(country__iexact=country)
    return JsonResponse([_league_to_dict(league) for league in qs], safe=False)


@require_GET
@_login_required_json
def championship_list(request):
    qs = _championship_with_related().order_by("league__level", "league__name")

    if season_id := request.GET.get("season_id"):
        qs = qs.filter(season_id=season_id)
    if league_id := request.GET.get("league_id"):
        qs = qs.filter(league_id=league_id)
    if country := request.GET.get("country"):
        qs = qs.filter(league__country__iexact=country)
    if status := request.GET.get("status"):
        qs = qs.filter(status=status)

    return JsonResponse([_championship_to_summary(ch) for ch in qs], safe=False)


@require_GET
@_login_required_json
def championship_detail(request, pk: int):
    try:
        championship = (
            _championship_with_related()
            .prefetch_related(
                Prefetch(
                    "championshipteam_set",
                    queryset=ChampionshipTeam.objects.select_related("team").annotate(
                        goal_diff=F("goals_for") - F("goals_against")
                    ),
                )
            )
            .get(pk=pk)
        )
    except Championship.DoesNotExist as exc:
        raise Http404("Championship not found") from exc

    standings_qs = sorted(
        championship.championshipteam_set.all(),
        key=lambda team: (team.points, team.goals_for - team.goals_against, team.goals_for),
        reverse=True,
    )
    total = len(standings_qs)
    standings = [
        _standing_to_dict(team, index + 1, total)
        for index, team in enumerate(standings_qs)
    ]

    payload = {
        "championship": _championship_to_summary(championship),
        "standings": standings,
    }
    return JsonResponse(payload)


@require_GET
@_login_required_json
def championship_matches(request, pk: int):
    try:
        championship = _championship_with_related().get(pk=pk)
    except Championship.DoesNotExist as exc:
        raise Http404("Championship not found") from exc

    matches = list(
        ChampionshipMatch.objects.filter(championship=championship)
        .select_related(
            "match",
            "match__home_team",
            "match__away_team",
        )
        .order_by("round", "match_day", "match__datetime")
    )

    return JsonResponse(
        {"matches": [_match_to_dict(match) for match in matches]},
    )


@require_GET
@_login_required_json
def my_championship(request):
    club = getattr(request.user, "club", None)
    if not club:
        raise Http404("Club not found for current user")

    try:
        championship = (
            _championship_with_related()
            .prefetch_related(
                Prefetch(
                    "championshipteam_set",
                    queryset=ChampionshipTeam.objects.select_related("team").annotate(
                        goal_diff=F("goals_for") - F("goals_against")
                    ),
                ),
                Prefetch(
                    "championshipmatch_set",
                    queryset=ChampionshipMatch.objects.select_related(
                        "match",
                        "match__home_team",
                        "match__away_team",
                    ).order_by("match__datetime", "round"),
                ),
            )
            .get(teams=club, season__is_active=True)
        )
    except Championship.DoesNotExist as exc:
        raise Http404("Championship not found for your club") from exc

    standings_qs = sorted(
        championship.championshipteam_set.all(),
        key=lambda team: (team.points, team.goals_for - team.goals_against, team.goals_for),
        reverse=True,
    )
    total = len(standings_qs)
    standings = [
        _standing_to_dict(team, index + 1, total)
        for index, team in enumerate(standings_qs)
    ]

    club_row = next((row for row in standings if row["team"]["id"] == club.id), None)
    club_position = club_row["position"] if club_row else None

    matches = list(championship.championshipmatch_set.all())
    upcoming = []
    finished = []
    schedule = []
    now = timezone.now()

    for item in matches:
        match_dict = _match_to_dict(item)
        schedule.append(match_dict)
        match_datetime = _match_date(item)
        if item.match.status == "finished" or match_datetime < now:
            if item.match.status == "finished":
                finished.append(match_dict)
        else:
            upcoming.append(match_dict)

    payload = {
        "championship": _championship_to_summary(championship),
        "standings": standings,
        "club_position": club_position,
        "schedule": schedule,
        "next_matches": upcoming[:5],
        "last_results": finished[-5:],
    }
    return JsonResponse(payload)
