from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.urls import reverse
from django.conf import settings
import json
from django.utils import timezone
from django.http import JsonResponse
from django.db import models
from django.db.models import Count
from django_countries import countries
from .models import Championship, Season, League

class ChampionshipListView(LoginRequiredMixin, ListView):
    model = Championship
    template_name = 'tournaments/championship_list.html'
    context_object_name = 'championships'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.applied_filters = {}

    def get_queryset(self):
        queryset = (
            Championship.objects.all()
            .select_related('league', 'season')
            .prefetch_related('teams')
            .annotate(team_count=Count('teams', distinct=True))
        )

        self.applied_filters = self._extract_filters()
        filters = self.applied_filters

        if filters['season']:
            queryset = queryset.filter(season_id=filters['season'])
        if filters['league']:
            queryset = queryset.filter(league_id=filters['league'])
        if filters['status']:
            queryset = queryset.filter(status=filters['status'])
        if filters['country']:
            queryset = queryset.filter(league__country__iexact=filters['country'])

        return queryset.order_by(
            'league__country',
            'league__level',
            'league__name',
            'season__start_date',
        )

    def _extract_filters(self):
        def to_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        raw_status = (self.request.GET.get('status') or '').strip()
        valid_statuses = {choice[0] for choice in Championship.STATUS_CHOICES}
        status = raw_status if raw_status in valid_statuses else None

        country = (self.request.GET.get('country') or '').strip()
        country = country.upper() if country else None

        return {
            'season': to_int(self.request.GET.get('season')),
            'league': to_int(self.request.GET.get('league')),
            'status': status,
            'country': country,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seasons_qs = Season.objects.order_by('-start_date')
        leagues_qs = League.objects.order_by('country', 'level', 'name')

        context['active_seasons'] = seasons_qs.filter(is_active=True)
        context['seasons'] = seasons_qs
        context['leagues'] = leagues_qs
        context['status_choices'] = Championship.STATUS_CHOICES

        country_codes = leagues_qs.values_list('country', flat=True).distinct()
        context['countries'] = [
            {'code': code, 'name': countries.name(code) if code else ''}
            for code in country_codes
        ]

        filters = self.applied_filters or self._extract_filters()
        context['filters'] = filters
        context['has_active_filters'] = any(filters.values())
        context['championship_count'] = context['championships'].count()

        return context

class ChampionshipDetailView(LoginRequiredMixin, DetailView):
    model = Championship
    template_name = 'tournaments/championship_detail.html'
    context_object_name = 'championship'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        standings_qs = (
            self.object.championshipteam_set
            .select_related('team')
            .annotate(goals_diff=models.F('goals_for') - models.F('goals_against'))
            .order_by('-points', '-goals_diff', '-goals_for')
        )
        standings = list(standings_qs)
        for idx, row in enumerate(standings, start=1):
            row.table_position = idx
        context['standings'] = standings
        context['has_standings'] = bool(standings)

        matches_qs = self.object.championshipmatch_set.select_related(
            'match',
            'match__home_team',
            'match__away_team'
        ).order_by('round', 'match_day', 'match__datetime')
        matches = list(matches_qs)

        now = timezone.now()
        recent_matches = []
        upcoming_matches = []
        calendar_events = []

        for match in matches:
            scheduled_dt = self._resolve_match_datetime(match)
            match.scheduled_datetime = scheduled_dt

            if scheduled_dt:
                calendar_events.append({
                    'id': match.id,
                    'title': f"{match.match.home_team} vs {match.match.away_team}",
                    'start': scheduled_dt.isoformat(),
                    'status': match.match.status,
                    'score': f"{match.match.home_score} - {match.match.away_score}" if match.match.status == 'finished' else None,
                    'url': reverse('matches:match_detail', args=[match.match.id]),
                    'className': f"match-{match.match.status}"
                })

            if match.match.status == 'finished' and scheduled_dt:
                recent_matches.append(match)
            elif scheduled_dt and scheduled_dt >= now:
                upcoming_matches.append(match)

        recent_matches.sort(key=lambda item: item.scheduled_datetime, reverse=True)
        upcoming_matches.sort(key=lambda item: item.scheduled_datetime)

        context['matches'] = matches
        context['recent_matches'] = recent_matches[:5]
        context['upcoming_matches'] = upcoming_matches[:5]
        context['has_matches'] = bool(matches)
        context['calendar_events'] = json.dumps(calendar_events)
        context['user_timezone'] = self.request.session.get('timezone', timezone.get_current_timezone_name())

        return context

    def _resolve_match_datetime(self, championship_match):
        match_obj = getattr(championship_match, 'match', None)
        dt = getattr(match_obj, 'datetime', None)

        if not dt:
            dt = getattr(championship_match, 'match_datetime', None)

        if dt and timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_default_timezone())

        return dt

class MyChampionshipView(LoginRequiredMixin, DetailView):
    model = Championship
    template_name = 'tournaments/my_championship.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'club'):
            messages.warning(request, "You need to create a club first.")
            return redirect('clubs:create_club')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        try:
            return Championship.objects.select_related(
                'league',
                'season'
            ).get(
                teams=self.request.user.club,
                season__is_active=True
            )
        except Championship.DoesNotExist:
            raise Http404("No championship found for your club")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        championship = self.object
        user_club = self.request.user.club

        # Get standings
        context['standings'] = championship.championshipteam_set.select_related(
            'team'
        ).order_by(
            '-points', 
            '-goals_for'
        )

        # Get team matches for display
        context['team_matches'] = championship.championshipmatch_set.filter(
            models.Q(match__home_team=user_club) | 
            models.Q(match__away_team=user_club)
        ).select_related(
            'match', 
            'match__home_team', 
            'match__away_team'
        ).order_by('match__datetime')

        return context

class ChampionshipCalendarView(LoginRequiredMixin, DetailView):
    model = Championship
    template_name = 'tournaments/championship_calendar.html'
    context_object_name = 'championship'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class SeasonListView(LoginRequiredMixin, ListView):
    model = Season
    template_name = 'tournaments/season_list.html'
    context_object_name = 'seasons'

class LeagueListView(LoginRequiredMixin, ListView):
    model = League
    template_name = 'tournaments/league_list.html'
    context_object_name = 'leagues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        countries = {}
        for league in self.get_queryset().order_by('country', 'level'):
            if league.country not in countries:
                countries[league.country] = []
            countries[league.country].append(league)
        context['countries'] = countries
        return context

def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect(request.POST.get('next', '/'))
    else:
        return redirect('/')

def get_championship_matches(request, pk):
    championship = Championship.objects.get(pk=pk)
    matches = championship.championshipmatch_set.all().select_related(
        'match', 
        'match__home_team', 
        'match__away_team'
    )
    
    match_data = [{
        'id': match.id,
        'round': match.round,
        'date': match.match.datetime.isoformat(),
        'home_team': match.match.home_team.name,
        'away_team': match.match.away_team.name,
        'status': match.match.status,
        'score': f"{match.match.home_score}-{match.match.away_score}" if match.match.status == 'finished' else None
    } for match in matches]
    
    return JsonResponse({'matches': match_data})
