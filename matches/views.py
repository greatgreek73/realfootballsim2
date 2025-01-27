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
from players.models import Player  # Для доступа к Player и sum_attributes
# Импорт Celery-задач
from .tasks import simulate_match_minute, broadcast_minute_events_in_chunks
from .utils import extract_player_id
from tournaments.models import Championship, League


def get_match_lineups(match):
    """
    Получает составы матча и связанных игроков оптимизированным способом.
    """
    home_lineup_list = []
    away_lineup_list = []

    # Домашний состав
    if match.home_lineup and isinstance(match.home_lineup, dict):
        # Если это вложенный словарь с 'lineup'
        if 'lineup' in match.home_lineup:
            lineup_dict = match.home_lineup['lineup']
        else:
            lineup_dict = match.home_lineup
        
        home_ids = []
        for slot_val in lineup_dict.values():
            player_id_str = extract_player_id(slot_val)
            if player_id_str and player_id_str.strip():
                try:
                    pid = int(player_id_str.strip())
                    if pid > 0:
                        home_ids.append(pid)
                except (ValueError, TypeError):
                    continue
        
        home_players = {str(p.id): p for p in Player.objects.filter(id__in=home_ids)}
        
        for slot_num in range(11):
            slot_key = str(slot_num)
            slot_val = lineup_dict.get(slot_key)
            player_id_str = extract_player_id(slot_val)
            player_obj = home_players.get(player_id_str) if player_id_str else None
            home_lineup_list.append((slot_key, player_obj))

    # Гостевой состав
    if match.away_lineup and isinstance(match.away_lineup, dict):
        if 'lineup' in match.away_lineup:
            lineup_dict = match.away_lineup['lineup']
        else:
            lineup_dict = match.away_lineup

        away_ids = []
        for slot_val in lineup_dict.values():
            player_id_str = extract_player_id(slot_val)
            if player_id_str and player_id_str.strip():
                try:
                    pid = int(player_id_str.strip())
                    if pid > 0:
                        away_ids.append(pid)
                except (ValueError, TypeError):
                    continue
        
        away_players = {str(p.id): p for p in Player.objects.filter(id__in=away_ids)}
        
        for slot_num in range(11):
            slot_key = str(slot_num)
            slot_val = lineup_dict.get(slot_key)
            player_id_str = extract_player_id(slot_val)
            player_obj = away_players.get(player_id_str) if player_id_str else None
            away_lineup_list.append((slot_key, player_obj))

    return home_lineup_list, away_lineup_list


# =========================
#   НОВАЯ ФУНКЦИЯ
# =========================
def get_best_players_by_line(club):
    """
    Возвращает словарь c ключами 'GK', 'DEF', 'MID', 'FWD':
      {
        'GK': лучший_вратарь_или_None,
        'DEF': лучший_защитник_или_None,
        'MID': лучший_полузащитник_или_None,
        'FWD': лучший_нападающий_или_None,
      }
    Лучший определяется по сумме всех характеристик (sum_attributes()).
    Опорники считаются защитниками, атакующие полузащитники считаются полузащитниками.
    """
    from players.models import get_player_line

    best = {
        'GK': (0, None),
        'DEF': (0, None),
        'MID': (0, None),
        'FWD': (0, None),
    }
    players = club.player_set.all()

    for p in players:
        line = get_player_line(p)  # Определяем GK/DEF/MID/FWD
        total = p.sum_attributes() # Сумма всех атрибутов
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

    # Получаем события матча
    match_events = match.events.order_by('minute')

    # Получаем составы (если нужно)
    home_lineup_list, away_lineup_list = get_match_lineups(match)

    # =========================
    #   ДОБАВЛЯЕМ ЛУЧШИХ ИГРОКОВ
    # =========================
    home_best = get_best_players_by_line(match.home_team)
    away_best = get_best_players_by_line(match.away_team)

    context = {
        'match': match,
        'match_events': match_events,
        'home_lineup_list': home_lineup_list,
        'away_lineup_list': away_lineup_list,
        # Новые ключи для лучших игроков:
        'home_best': home_best,
        'away_best': away_best,
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
            status='scheduled',
            current_minute=0,
            home_tactic='balanced',
            away_tactic='balanced',
        )
        
        # Предматчевая подготовка
        from .match_preparation import PreMatchPreparation
        prep = PreMatchPreparation(match)
        if not prep.prepare_match():
            errors = prep.get_validation_errors()
            messages.error(request, f"Match preparation failed: {'; '.join(errors)}")
            match.delete()
            return redirect('clubs:club_detail', pk=club.id)
            
        match.status = 'in_progress'
        match.save()
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
