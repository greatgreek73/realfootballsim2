# C:\realfootballsim\matches\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
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


def _extract_player_id(slot_val):
    """
    Универсальная функция, которая извлекает playerId как строку
    из любого формата слота (старого или нового).
      - Старый формат: slot_val = "8012" (str)
      - Новый формат: slot_val = {"playerId": "8012", ...}
    Возвращает строку (например, "8012") или None.
    """
    if isinstance(slot_val, dict):
        # Новый формат
        return slot_val.get("playerId")  # может быть "8012" или None
    else:
        # Старый формат (просто строка)
        return slot_val


def get_match_lineups(match):
    """
    Получает составы (home_lineup_list, away_lineup_list) и связанных игроков.
    Каждый из них — список кортежей (slot_key, player_obj).
    """
    home_lineup_list = []
    away_lineup_list = []

    # --------------------------
    # Обработка домашнего состава
    # --------------------------
    if match.home_lineup and isinstance(match.home_lineup, dict):
        # Если это "вложенный" формат с ключом 'lineup'
        if 'lineup' in match.home_lineup:
            lineup_dict = match.home_lineup['lineup']
        else:
            lineup_dict = match.home_lineup

        # 1) Собираем все playerId (строки) в множество
        home_id_strings = set()
        for slot_val in lineup_dict.values():
            pid_str = _extract_player_id(slot_val)
            if pid_str:
                home_id_strings.add(pid_str)

        # 2) Загружаем всех игроков одним запросом
        #    и делаем словарь по ключу (строковому id).
        home_players = {
            str(p.id): p
            for p in Player.objects.filter(id__in=home_id_strings)
        }

        # 3) Собираем home_lineup_list в порядке слотов 0..10
        for slot_num in range(11):
            slot_key = str(slot_num)
            slot_val = lineup_dict.get(slot_key)
            # Извлекаем playerId из слота
            pid_str = _extract_player_id(slot_val)

            # Ищем Player в словаре
            player_obj = None
            if pid_str:
                player_obj = home_players.get(pid_str)

            home_lineup_list.append((slot_key, player_obj))

    # --------------------------
    # Обработка гостевого состава
    # --------------------------
    if match.away_lineup and isinstance(match.away_lineup, dict):
        if 'lineup' in match.away_lineup:
            lineup_dict = match.away_lineup['lineup']
        else:
            lineup_dict = match.away_lineup

        away_id_strings = set()
        for slot_val in lineup_dict.values():
            pid_str = _extract_player_id(slot_val)
            if pid_str:
                away_id_strings.add(pid_str)

        away_players = {
            str(p.id): p
            for p in Player.objects.filter(id__in=away_id_strings)
        }

        for slot_num in range(11):
            slot_key = str(slot_num)
            slot_val = lineup_dict.get(slot_key)
            pid_str = _extract_player_id(slot_val)

            player_obj = None
            if pid_str:
                player_obj = away_players.get(pid_str)

            away_lineup_list.append((slot_key, player_obj))

    return home_lineup_list, away_lineup_list


@login_required
def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    
    # Получаем события матча
    match_events = match.events.order_by('minute')
    
    # Получаем составы
    home_lineup_list, away_lineup_list = get_match_lineups(match)

    # Проверяем, является ли пользователь членом одной из команд (для UI)
    is_user_team = (
        request.user.is_authenticated
        and (
            request.user.club == match.home_team
            or request.user.club == match.away_team
        )
    )
    
    context = {
        'match': match,
        'match_events': match_events,
        'is_user_team': is_user_team,
        'home_lineup_list': home_lineup_list,
        'away_lineup_list': away_lineup_list
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
            return Match.objects.filter(
                championshipmatch__championship_id=championship_id
            ).order_by('championshipmatch__round', 'datetime')

        return Match.objects.filter(
            Q(home_team=self.request.user.club) | 
            Q(away_team=self.request.user.club)
        )


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
    if match_id == 0:
        club = request.user.club
        opponent = Club.objects.filter(is_bot=True).exclude(id=club.id).order_by('?').first()
        if not opponent:
            return render(request, 'matches/no_opponent.html', {'club': club})
        
        match = Match.objects.create(
            home_team=club,
            away_team=opponent,
            datetime=timezone.now(),
            status='in_progress',
            current_minute=0,
            home_tactic='balanced',
            away_tactic='balanced',
        )
        match_id = match.id
    
    return redirect('matches:match_detail', pk=match_id)


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
