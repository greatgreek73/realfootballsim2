from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q

from .models import Match, MatchEvent
from clubs.models import Club
from players.models import Player
# Импорт Celery-задач
from .tasks import simulate_match_minute, broadcast_minute_events_in_chunks
from .utils import extract_player_id
from tournaments.models import Championship, League
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_lineups_from_json(lineup_json):
    """
    Преобразует JSON/словарь состава (как в match.home_lineup) в список (slot, player).
    Возвращает список вида [(slot_key, player_obj), ...].
    """
    lineup_list = []
    if not lineup_json or not isinstance(lineup_json, dict):
        return lineup_list

    # Если есть вложенный 'lineup'
    if 'lineup' in lineup_json:
        real_lineup = lineup_json['lineup']
    else:
        real_lineup = lineup_json

    # Собираем ID игроков
    player_ids = []
    for slot_val in real_lineup.values():
        pid_str = extract_player_id(slot_val)
        if pid_str and pid_str.isdigit():
            player_ids.append(int(pid_str))

    # Берём объекты Player одним запросом
    players_by_id = {p.id: p for p in Player.objects.filter(id__in=player_ids)}

    # Формируем 11 слотов (0..10)
    for slot_num in range(11):
        slot_key = str(slot_num)
        val = real_lineup.get(slot_key)
        pid_str = extract_player_id(val)
        player_obj = None
        if pid_str and pid_str.isdigit():
            pid = int(pid_str)
            player_obj = players_by_id.get(pid)
        lineup_list.append((slot_key, player_obj))

    return lineup_list


def get_match_lineups(match):
    """
    Получает составы (home_lineup_list, away_lineup_list) из match.home_lineup / match.away_lineup.
    """
    home_lineup_list = get_lineups_from_json(match.home_lineup)
    away_lineup_list = get_lineups_from_json(match.away_lineup)
    return home_lineup_list, away_lineup_list


def get_best_players_by_line(club):
    """
    Возвращает dict { 'GK': Player|None, 'DEF': ..., 'MID': ..., 'FWD': ... }
    с лучшими игроками клуба по каждой линии. 
    """
    from players.models import get_player_line

    best = {
        'GK': (0, None),
        'DEF': (0, None),
        'MID': (0, None),
        'FWD': (0, None),
    }
    for p in club.player_set.all():
        line = get_player_line(p)
        total = p.sum_attributes()
        if total > best[line][0]:
            best[line] = (total, p)

    return {
        'GK': best['GK'][1],
        'DEF': best['DEF'][1],
        'MID': best['MID'][1],
        'FWD': best['FWD'][1],
    }


@login_required
def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    match_events = match.events.order_by('minute')

    # Текущие составы
    home_lineup_list, away_lineup_list = get_match_lineups(match)

    # Лучшие игроки (для блока, если match.status == 'scheduled')
    home_best = get_best_players_by_line(match.home_team)
    away_best = get_best_players_by_line(match.away_team)

    # -----------------------------------------------------
    # 1) Если match.status == 'scheduled', 
    #    ищем последний сыгранный матч для home_team
    # -----------------------------------------------------
    home_prev_match = None
    home_prev_lineup_list = []
    if match.status == 'scheduled':
        home_prev_match = (
            Match.objects.filter(
                status='finished',
                datetime__lt=match.datetime
            )
            .filter(Q(home_team=match.home_team) | Q(away_team=match.home_team))
            .order_by('-datetime')
            .first()
        )
        if home_prev_match:
            # Если в home_prev_match home_team == match.home_team,
            #    значит lineups для "домашней" стороны
            # Иначе берем away_lineup.
            if home_prev_match.home_team == match.home_team:
                home_prev_lineup_list = get_lineups_from_json(home_prev_match.home_lineup)
            else:
                home_prev_lineup_list = get_lineups_from_json(home_prev_match.away_lineup)

    # -----------------------------------------------------
    # 2) Если match.status == 'scheduled',
    #    ищем последний сыгранный матч для away_team
    # -----------------------------------------------------
    away_prev_match = None
    away_prev_lineup_list = []
    if match.status == 'scheduled':
        away_prev_match = (
            Match.objects.filter(
                status='finished',
                datetime__lt=match.datetime
            )
            .filter(Q(home_team=match.away_team) | Q(away_team=match.away_team))
            .order_by('-datetime')
            .first()
        )
        if away_prev_match:
            if away_prev_match.home_team == match.away_team:
                away_prev_lineup_list = get_lineups_from_json(away_prev_match.home_lineup)
            else:
                away_prev_lineup_list = get_lineups_from_json(away_prev_match.away_lineup)

    context = {
        'match': match,
        'match_events': match_events,

        'home_lineup_list': home_lineup_list,
        'away_lineup_list': away_lineup_list,

        'home_best': home_best,
        'away_best': away_best,

        # Предыдущие матчи каждой команды
        'home_prev_match': home_prev_match,
        'home_prev_lineup_list': home_prev_lineup_list,

        'away_prev_match': away_prev_match,
        'away_prev_lineup_list': away_prev_lineup_list,
    }

    return render(request, 'matches/match_detail.html', context)


class CreateMatchView(CreateView):
    model = Match
    fields = ['home_team', 'away_team', 'datetime']
    template_name = 'matches/create_match.html'

    def form_valid(self, form):
        match = form.save()
        return redirect(reverse('matches:match_detail', kwargs={'pk': match.pk}))


class MatchListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'

    def get_queryset(self):
        championship_id = self.kwargs.get('championship_id')
        if championship_id:
            matches = Match.objects.filter(
                championshipmatch__championship_id=championship_id
            ).order_by('championshipmatch__round', 'datetime')
            paginator = Paginator(matches, 7)
            pageNumber = int(self.request.GET.get('page') or 1)
            if pageNumber > paginator.num_pages:
                pageNumber = paginator.num_pages
            return paginator.page(pageNumber)

        matches = Match.objects.filter(
            Q(home_team=self.request.user.club) |
            Q(away_team=self.request.user.club)
        )
        paginator = Paginator(matches, 7)
        pageNumber = int(self.request.GET.get('page') or 1)
        if pageNumber > paginator.num_pages:
            pageNumber = paginator.num_pages
        return paginator.page(pageNumber)




@login_required
def get_match_events(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    events = match.events.order_by('minute').values('minute', 'event_type', 'description')
    return JsonResponse({
        'events': list(events),
        'match': {
            'home_team': match.home_team.name,
            'away_team': match.away_team.name,
            'final_score': {
                'home': match.home_score,
                'away': match.away_score
            }
        }
    })


@login_required
def simulate_match_view(request, match_id):
    print("dddd")
    return true


@login_required
def simulate_match_minute_view(request, match_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], "This endpoint requires POST request")

    match = get_object_or_404(Match, id=match_id)
    simulate_match_minute.delay(match_id)
    next_minute = match.current_minute + 1
    broadcast_minute_events_in_chunks.delay(match_id, next_minute, duration=10)

    return JsonResponse({
        'status': 'ok',
        'message': f"Requested simulation of 1 minute for match {match_id} + chunked broadcast."
    })
