from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
import logging
from .models import Match, MatchEvent, NarrativeEvent, PlayerRivalry, TeamChemistry, CharacterEvolution
from clubs.models import Club
from players.models import Player
# Импорт Celery-задач
from django.conf import settings
from .utils import extract_player_id
from tournaments.models import Championship, League
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .match_preparation import PreMatchPreparation
from django.views.decorators.http import require_http_methods
from .narrative_system import NarrativeAIEngine, RivalryManager, ChemistryCalculator



logger = logging.getLogger('match_creation')



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


def enrich_events_with_narrative_context(match_events, match):
    """
    Обогащает события матча нарративным контекстом:
    - Добавляет информацию о соперничестве игроков
    - Определяет химию между игроками
    - Отмечает моменты эволюции характера
    - Добавляет нарративные события
    """
    enriched_events = []
    
    # Получаем нарративные события для этого матча
    narrative_events = NarrativeEvent.objects.filter(match=match).select_related(
        'primary_player', 'secondary_player'
    )
    narrative_by_minute = {ne.minute: ne for ne in narrative_events}
    
    # Получаем эволюции характера для этого матча
    character_evolutions = CharacterEvolution.objects.filter(match=match).select_related('player')
    evolutions_by_minute = {}
    for evo in character_evolutions:
        # Для простоты, связываем эволюции с последней минутой матча
        # В реальной реализации можно добавить поле minute в CharacterEvolution
        minute = getattr(evo, 'minute', 90)  # По умолчанию 90-я минута
        if minute not in evolutions_by_minute:
            evolutions_by_minute[minute] = []
        evolutions_by_minute[minute].append(evo)
    
    for event in match_events:
        # Создаем обогащенное событие
        enriched_event = {
            'original_event': event,
            'minute': event.minute,
            'event_type': event.event_type,
            'description': event.description,
            'player': event.player,
            'related_player': event.related_player,
            'personality_reason': getattr(event, 'personality_reason', None),
            'narrative_context': {},
        }
        
        # Проверяем наличие нарративного события
        if event.minute in narrative_by_minute:
            narrative_event = narrative_by_minute[event.minute]
            enriched_event['narrative_context']['narrative_event'] = narrative_event
            enriched_event['narrative_context']['has_narrative'] = True
            enriched_event['narrative_context']['narrative_importance'] = narrative_event.importance
            enriched_event['narrative_context']['narrative_type'] = narrative_event.event_type
        
        # Проверяем эволюцию характера
        if event.minute in evolutions_by_minute:
            enriched_event['narrative_context']['character_evolutions'] = evolutions_by_minute[event.minute]
            enriched_event['narrative_context']['has_character_growth'] = True
        
        # Проверяем соперничество между игроками
        if event.player and event.related_player:
            rivalry = RivalryManager.get_rivalry_between(event.player, event.related_player)
            if rivalry:
                enriched_event['narrative_context']['rivalry'] = rivalry
                enriched_event['narrative_context']['has_rivalry'] = True
                enriched_event['narrative_context']['rivalry_intensity'] = rivalry.intensity
        
        # Проверяем химию между игроками (только для игроков одной команды)
        if (event.player and event.related_player and 
            event.player.club == event.related_player.club):
            chemistry = ChemistryCalculator.get_chemistry_between(event.player, event.related_player)
            if chemistry:
                enriched_event['narrative_context']['chemistry'] = chemistry
                enriched_event['narrative_context']['has_chemistry'] = True
                enriched_event['narrative_context']['chemistry_strength'] = chemistry.strength
        
        # Определяем общую важность события для нарратива
        narrative_importance = 'normal'
        if enriched_event['narrative_context'].get('has_narrative'):
            narrative_importance = enriched_event['narrative_context']['narrative_importance']
        elif enriched_event['narrative_context'].get('has_rivalry') and enriched_event['narrative_context']['rivalry_intensity'] in ['strong', 'intense']:
            narrative_importance = 'significant'
        elif enriched_event['narrative_context'].get('has_chemistry') and enriched_event['narrative_context']['chemistry_strength'] > 0.7:
            narrative_importance = 'minor'
        elif enriched_event['narrative_context'].get('has_character_growth'):
            narrative_importance = 'minor'
        
        enriched_event['narrative_context']['overall_importance'] = narrative_importance
        enriched_events.append(enriched_event)
    
    return enriched_events


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
    logger.info(f'[match_detail] Старт обработки запроса на матч ID={pk} от пользователя {request.user.username}')

    match = get_object_or_404(Match, pk=pk)
    logger.info(f'[match_detail] Найден матч: {match.home_team.name} vs {match.away_team.name}, статус: {match.status}')

    match_events = match.events.order_by('minute')
    logger.info(f'[match_detail] Загружено событий: {match_events.count()}')
    
    # Обогащаем события нарративным контекстом
    try:
        enriched_match_events = enrich_events_with_narrative_context(match_events, match)
        logger.info(f'[match_detail] События обогащены нарративным контекстом')
    except Exception as e:
        logger.warning(f'[match_detail] Ошибка обогащения событий: {e}')
        # Fallback: создаем простую версию без нарративного контекста
        enriched_match_events = []
        for event in match_events:
            enriched_match_events.append({
                'original_event': event,
                'minute': event.minute,
                'event_type': event.event_type,
                'description': event.description,
                'player': event.player,
                'related_player': event.related_player,
                'narrative_context': {'overall_importance': 'normal'},
            })

    home_lineup_list, away_lineup_list = get_match_lineups(match)
    logger.info(f'[match_detail] Составы получены: домашняя = {len(home_lineup_list)}, гостевая = {len(away_lineup_list)}')

    if len(home_lineup_list) < 11:
        logger.warning(f'[match_detail] Недостаточно игроков в составе домашней команды: {len(home_lineup_list)}')
    if len(away_lineup_list) < 11:
        logger.warning(f'[match_detail] Недостаточно игроков в составе гостевой команды: {len(away_lineup_list)}')

    home_best = get_best_players_by_line(match.home_team)
    away_best = get_best_players_by_line(match.away_team)
    logger.info(f'[match_detail] Получены лучшие игроки: home={match.home_team.name}, away={match.away_team.name}')

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
            logger.info(f'[match_detail] Найден предыдущий матч для домашней команды: ID={home_prev_match.id}')
            if home_prev_match.home_team == match.home_team:
                home_prev_lineup_list = get_lineups_from_json(home_prev_match.home_lineup)
            else:
                home_prev_lineup_list = get_lineups_from_json(home_prev_match.away_lineup)
        else:
            logger.warning(f'[match_detail] Предыдущий матч для домашней команды не найден')

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
            logger.info(f'[match_detail] Найден предыдущий матч для гостевой команды: ID={away_prev_match.id}')
            if away_prev_match.home_team == match.away_team:
                away_prev_lineup_list = get_lineups_from_json(away_prev_match.home_lineup)
            else:
                away_prev_lineup_list = get_lineups_from_json(away_prev_match.away_lineup)
        else:
            logger.warning(f'[match_detail] Предыдущий матч для гостевой команды не найден')

    # Получаем нарративную сводку матча
    try:
        narrative_summary = NarrativeAIEngine.get_match_narrative_summary(match)
        logger.info(f'[match_detail] Получена нарративная сводка: {narrative_summary["total_events"]} событий')
    except Exception as e:
        logger.warning(f'[match_detail] Ошибка получения нарративной сводки: {e}')
        narrative_summary = {
            'narrative_events': [],
            'character_evolutions': [],
            'total_events': 0,
            'major_events': 0
        }

    context = {
        'match': match,
        'match_events': match_events,
        'enriched_match_events': enriched_match_events,
        'narrative_summary': narrative_summary,
        'home_lineup_list': home_lineup_list,
        'away_lineup_list': away_lineup_list,
        'home_best': home_best,
        'away_best': away_best,
        'home_prev_match': home_prev_match,
        'home_prev_lineup_list': home_prev_lineup_list,
        'away_prev_match': away_prev_match,
        'away_prev_lineup_list': away_prev_lineup_list,
        # Pass duration of one simulated minute to the template
        'match_minute_seconds': settings.MATCH_MINUTE_REAL_SECONDS,
    }

    logger.info(f'[match_detail] Контекст подготовлен. Рендер страницы match_detail.html для матча ID={pk}')
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
        logger.info(f'Кнопка "Create New Match" нажата пользователем {request.user.username}')

        if match_id == 0:
            logger.info('Режим создания нового тестового матча (match_id == 0) активирован')

            # Получаем клуб пользователя
            club = request.user.club
            logger.info(f'Клуб пользователя: {club.name} (ID={club.id})')

            # Находим случайного бота-соперника
            opponent = Club.objects.filter(is_bot=True).exclude(id=club.id).order_by('?').first()
            if not opponent:
                logger.warning(f'Не удалось найти бота-соперника для клуба {club.name}')
                return render(request, 'matches/no_opponent.html', {'club': club})

            logger.info(f'Выбран соперник-бот: {opponent.name} (ID={opponent.id})')

            # Создаём матч
            match = Match.objects.create(
                home_team=club,
                away_team=opponent,
                datetime=timezone.now(),
                status='scheduled',
                current_minute=1,
                home_tactic='balanced',
                away_tactic='balanced',
            )
            logger.info(f'Создан матч ID={match.id} между {club.name} и {opponent.name}')

            # Предматчевая подготовка
            prep = PreMatchPreparation(match)
            if not prep.prepare_match():
                errors = prep.get_validation_errors()
                logger.error(f'Ошибка подготовки матча ID={match.id}: {errors}')
                messages.error(request, f"Match preparation failed: {'; '.join(errors)}")
                match.delete()
                return redirect('clubs:club_detail', pk=club.id)

            match.status = 'in_progress'
            match.save()
            logger.info(f'[VIEW] Match ID={match.id} set to in_progress')
            logger.info(f'Матч ID={match.id} успешно подготовлен и переведён в статус "in_progress"')

            match_id = match.id

        # Завершающее перенаправление на страницу матча
        logger.info(f'Перенаправление пользователя на страницу матча ID={match_id}')
        return redirect('matches:match_detail', pk=match_id)


@login_required
@require_http_methods(["POST"])
def substitute_player(request, match_id):
    """Handle a simple substitution triggered from the live match page."""
    match = get_object_or_404(Match, pk=match_id)
    if match.status != 'in_progress':
        return JsonResponse({"success": False, "error": "Match not running"}, status=400)

    try:
        payload = json.loads(request.body)
        out_player_id = int(payload.get('out_player_id', 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"success": False, "error": "Invalid data"}, status=400)

    player = Player.objects.filter(id=out_player_id).first()
    if not player:
        return JsonResponse({"success": False, "error": "Player not found"}, status=404)

    MatchEvent.objects.create(
        match=match,
        minute=match.current_minute,
        event_type='substitution',
        player=player,
        description=f"Substitution: {player.full_name} leaves the pitch"
    )

    if match.st_injury > 0:
        match.st_injury -= 1
    match.save(update_fields=["st_injury"])

    return JsonResponse({"success": True})
