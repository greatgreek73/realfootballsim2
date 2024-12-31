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

# Импорт Celery-задач
from .tasks import simulate_match_minute, broadcast_minute_events_in_chunks

##############################
#  ВАЖНО: добавим импорт Player
##############################
from players.models import Player


class CreateMatchView(CreateView):
    model = Match
    fields = ['home_team', 'away_team', 'datetime']
    template_name = 'matches/create_match.html'

    def form_valid(self, form):
        match = form.save()
        return redirect(reverse('matches:match_detail', kwargs={'pk': match.pk}))


class MatchDetailView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'matches/match_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.object  # Текущий матч

        # События матча (у вас уже было)
        context['match_events'] = match.events.order_by('minute')

        # Проверяем, относится ли клуб пользователя к одному из участников матча
        context['is_user_team'] = (
            self.request.user.is_authenticated
            and (
                self.request.user.club == match.home_team
                or self.request.user.club == match.away_team
            )
        )

        ############################################################
        # Новый блок: загрузка составов (home_lineup / away_lineup)
        ############################################################
        home_lineup_list = []
        away_lineup_list = []

        # HOME LINEUP
        if match.home_lineup and isinstance(match.home_lineup, dict):
            # Получаем id игроков (в JSON лежат строки "101", "102"...)
            home_ids = [int(val) for val in match.home_lineup.values()]
            # Тянем объекты Player одним запросом
            home_players_qs = Player.objects.filter(id__in=home_ids)
            home_dict = {p.id: p for p in home_players_qs}
            
            # Собираем в порядке слотов "0".."10"
            for slot_key, pid_str in sorted(match.home_lineup.items(), key=lambda x: x[0]):
                pid = int(pid_str)
                player_obj = home_dict.get(pid)
                # (slot_key, player_obj) => например ("0", Player(...))
                home_lineup_list.append((slot_key, player_obj))

        # AWAY LINEUP
        if match.away_lineup and isinstance(match.away_lineup, dict):
            away_ids = [int(val) for val in match.away_lineup.values()]
            away_players_qs = Player.objects.filter(id__in=away_ids)
            away_dict = {p.id: p for p in away_players_qs}

            for slot_key, pid_str in sorted(match.away_lineup.items(), key=lambda x: x[0]):
                pid = int(pid_str)
                player_obj = away_dict.get(pid)
                away_lineup_list.append((slot_key, player_obj))

        # Передаём в шаблон
        context['home_lineup_list'] = home_lineup_list
        context['away_lineup_list'] = away_lineup_list
        ############################################################

        return context


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

        # Если нет championship_id, показываем матчи команды пользователя
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
    """
    Создаёт тестовый матч, если match_id=0.
    Иначе просто редиректит на страницу матча.
    """
    if match_id == 0:
        # Получаем клуб пользователя
        club = request.user.club
        # Выбираем случайного бота-соперника
        opponent = Club.objects.filter(is_bot=True).exclude(id=club.id).order_by('?').first()
        if not opponent:
            return render(request, 'matches/no_opponent.html', {'club': club})
        
        # Создаем новый матч и сразу ставим его in_progress
        match = Match.objects.create(
            home_team=club,
            away_team=opponent,
            datetime=timezone.now(),
            status='in_progress',
            current_minute=0
        )
        match_id = match.id
    
    # Редирект на страницу матча
    return redirect('matches:match_detail', pk=match_id)


@login_required
def simulate_match_minute_view(request, match_id):
    """
    Пример ручного вызова симуляции ОДНОЙ виртуальной минуты:
      1) Запустить задачу Celery на simulate_match_minute
      2) Запустить задачу Celery на "chunked" broadcast (за 10 секунд) 
         событий этой минуты
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], "This endpoint requires POST request")

    match = get_object_or_404(Match, id=match_id)

    # Запускаем задачу симуляции одной минуты
    simulate_match_minute.delay(match_id)

    # В этот момент match.current_minute ещё старый (до симуляции),
    # но мы предполагаем, что за "текущую" минуту (match.current_minute+1)
    # будут созданы события.
    next_minute = match.current_minute + 1

    # Запускаем задачу "пошаговой" рассылки событий этой минуты
    broadcast_minute_events_in_chunks.delay(match_id, next_minute, duration=10)

    return JsonResponse({
        'status': 'ok',
        'message': f"Requested simulation of 1 minute for match {match_id} + chunked broadcast."
    })
