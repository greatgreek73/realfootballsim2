import random
import logging

from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Match, MatchEvent
from .player_agent import PlayerAgent
from players.models import Player

# === Добавляем импорт класса, отвечающего за авто-выбор состава ===
from .match_preparation import PreMatchPreparation

logger = logging.getLogger(__name__)


class MatchSimulation:
    # Словарь допустимых позиций для каждого типа слота
    SLOT_POSITION_MAPPING = {
        "goalkeeper": ["Goalkeeper"],
        "defender": ["Right Back", "Left Back", "Center Back", "Defensive Midfielder"],
        "midfielder": ["Central Midfielder", "Left Midfielder", "Right Midfielder", "Defensive Midfielder", "Attacking Midfielder"],
        "forward": ["Center Forward", "Attacking Midfielder"]
    }

    def __init__(self, match: Match):
        # === Добавляем вызов предматчевой подготовки, чтобы у ботов генерировался состав ===
        prep = PreMatchPreparation(match)
        prep.prepare_match()
        # === Конец добавки ===

        self.match = match

        # Изначально, в базе у нас:
        # match.home_lineup = {
        #   "lineup": {
        #       "0": { "playerId": "8001", "slotType": "goalkeeper", "slotLabel": "GK" },
        #       "1": { "playerId": "8002", "slotType": "defender",   "slotLabel": "LB" },
        #       ...
        #   },
        #   "tactic": "balanced"
        # }
        #
        # Аналогично для match.away_lineup

        self.match_stats = {
            'home': {
                'possession': 50,
                'shots': 0,
                'goals': 0,
                'passes': 0,
                'tackles': 0,
                'team_attack': 0,
                'team_defense': 0,
                'team_midfield': 0,
                'tactics': 'balanced',  # по умолчанию
            },
            'away': {
                'possession': 50,
                'shots': 0,
                'goals': 0,
                'passes': 0,
                'tackles': 0,
                'team_attack': 0,
                'team_defense': 0,
                'team_midfield': 0,
                'tactics': 'balanced',
            },
        }

        # При инициализации сразу прочитаем tactic:
        if isinstance(self.match.home_lineup, dict):
            self.match_stats['home']['tactics'] = self.match.home_lineup.get('tactic', 'balanced')
        if isinstance(self.match.away_lineup, dict):
            self.match_stats['away']['tactics'] = self.match.away_lineup.get('tactic', 'balanced')

        # Разберём home_lineup
        home_lineup_dict = {}
        if self.match.home_lineup and isinstance(self.match.home_lineup, dict):
            home_lineup_dict = self.match.home_lineup.get('lineup', {})
        away_lineup_dict = {}
        if self.match.away_lineup and isinstance(self.match.away_lineup, dict):
            away_lineup_dict = self.match.away_lineup.get('lineup', {})

        # Сохраним в self.home_slots / self.away_slots
        self.home_slots = self._build_slot_map(home_lineup_dict)
        self.away_slots = self._build_slot_map(away_lineup_dict)

        # Для удобства также соберём списки игроков (их атрибутов) и рассчитаем командные параметры
        self._calculate_team_parameters()

        # Изначально "владелец мяча" и "зона" не заданы
        self.ball_owner = None
        self.current_zone = None

        # Подготовим списки минут, когда возникают опасные моменты
        self._setup_moments()

    def _build_slot_map(self, lineup_dict):
        """
        На входе: { "0": { "playerId": "8001", "slotType": "goalkeeper", ... }, "1": {...}, ... }
        Возвращаем: dict, ключ=строка слота, значение={
           "playerObj": <Player>,
           "agent": <PlayerAgent>,
           "slotType": ...,
           "slotLabel": ...,
        }
        """
        result = {}
        for slot_index, slot_info in lineup_dict.items():
            # slot_info => {playerId, slotType, slotLabel, ...}
            player_id_str = slot_info.get("playerId")
            if not player_id_str:
                continue
            try:
                player_id = int(player_id_str)
                player_obj = Player.objects.get(pk=player_id)
            except (ValueError, Player.DoesNotExist):
                logger.warning(f"Slot {slot_index}: invalid playerId={player_id_str}, skipping.")
                continue

            agent = PlayerAgent(player_obj)
            result[slot_index] = {
                "playerObj": player_obj,
                "agent": agent,
                "slotType": slot_info.get("slotType"),    # "goalkeeper", "defender", ...
                "slotLabel": slot_info.get("slotLabel"),  # "GK", "LB", "CB", ...
            }
        return result

    def _calculate_team_parameters(self):
        """
        Для каждой команды (home/away) вычисляем "team_attack", "team_defense", "team_midfield"
        на основе игроков, лежащих в self.home_slots / self.away_slots.
        """
        self.match_stats['home']['team_attack'] = self._calculate_team_parameter(self.home_slots, 'attack')
        self.match_stats['home']['team_defense'] = self._calculate_team_parameter(self.home_slots, 'defense')
        self.match_stats['home']['team_midfield'] = self._calculate_team_parameter(self.home_slots, 'midfield')

        self.match_stats['away']['team_attack'] = self._calculate_team_parameter(self.away_slots, 'attack')
        self.match_stats['away']['team_defense'] = self._calculate_team_parameter(self.away_slots, 'defense')
        self.match_stats['away']['team_midfield'] = self._calculate_team_parameter(self.away_slots, 'midfield')

    def _calculate_team_parameter(self, slots_dict, parameter_type):
        """
        Рассчитываем некое «среднее» параметра (атака/защита/центр) по набору игроков.
        Применяем штраф, если игрок не на своей позиции.
        """
        total = 0
        count = 0

        for slot_idx, slot_data in slots_dict.items():
            player = slot_data["playerObj"]
            slot_type = slot_data["slotType"]  # "goalkeeper", "defender", ...
            experience_multiplier = 1 + player.experience * 0.01

            # Базовые значения в зависимости от типа параметра
            if parameter_type == 'attack':
                base_value = player.finishing + player.heading + player.long_range
            elif parameter_type == 'defense':
                base_value = player.marking + player.tackling + player.heading
            else:  # 'midfield'
                base_value = player.passing + player.vision + player.work_rate

            # Проверяем, подходит ли позиция игрока для данного слота
            penalty_coefficient = 1.0
            allowed_positions = self.SLOT_POSITION_MAPPING.get(slot_type, [])
            if player.position not in allowed_positions:
                # Штраф 30% если игрок не на своей позиции
                penalty_coefficient = 0.7

            final_value = base_value * experience_multiplier * penalty_coefficient
            weight = 1.0  # Единый вес для всех игроков
            
            total += (final_value * weight)
            count += weight

        if count > 0:
            return round(total / count)
        else:
            return 50

    def _setup_moments(self):
        """
        Определяем, на каких минутах будет опасный момент у home/away (упрощённо).
        """
        base_min, base_max = 10, 20
        home_strength = (self.match_stats['home']['team_attack'] + self.match_stats['home']['team_midfield']) / 2
        away_strength = (self.match_stats['away']['team_attack'] + self.match_stats['away']['team_midfield']) / 2

        home_factor = min(home_strength / 100, 1.0)
        away_factor = min(away_strength / 100, 1.0)

        home_chances = int(base_min + (base_max - base_min) * home_factor)
        away_chances = int(base_min + (base_max - base_min) * away_factor)

        all_minutes = list(range(1, 90))
        random.shuffle(all_minutes)

        self.home_moments_minutes = sorted(all_minutes[:home_chances])
        self.away_moments_minutes = sorted(all_minutes[home_chances : home_chances + away_chances])

    def create_match_event(self, minute, event_type, agent, description):
        """
        Создаём MatchEvent в БД (запись о событии).
        agent.player_model — ссылка на Player (или None).
        """
        player_model = agent.player_model if agent else None
        MatchEvent.objects.create(
            match=self.match,
            minute=minute,
            event_type=event_type,
            player=player_model,
            description=description
        )

    def simulate_minute(self, minute):
        """
        Логика "1 минута матча": упрощённая схема выбора атакующей команды и рандомного игрока.
        """
        if minute in self.home_moments_minutes:
            attacking_team = 'home'
        elif minute in self.away_moments_minutes:
            attacking_team = 'away'
        else:
            # Ни у кого нет опасного момента
            return

        self.create_match_event(minute, 'info', None,
                                f"MOMENT at minute {minute}: {attacking_team.upper()} tries to attack!")

        # Соберём список «подходящих» слотов для атаки.
        if attacking_team == 'home':
            slot_map = self.home_slots
            defending_team = 'away'
        else:
            slot_map = self.away_slots
            defending_team = 'home'

        attacking_slots = [
            idx
            for idx, data in slot_map.items()
            if data["slotType"] in ('midfielder', 'forward')
        ]

        if not attacking_slots:
            logger.warning(f"No attacking slots found for {attacking_team}.")
            return

        chosen_slot_index = random.choice(attacking_slots)
        slot_data = slot_map[chosen_slot_index]
        agent = slot_data["agent"]

        self.create_match_event(
            minute,
            'info',
            agent,
            f"Ball owned by {agent.full_name} (slot {slot_data['slotLabel']})"
        )

        # Определим вероятность гола (упрощённо 25%)
        goal_probability = 0.25

        # Усилим шанс, если это «forward»
        if slot_data["slotType"] == 'forward':
            goal_probability += 0.10  # +10% если тип «forward»

        if random.random() < goal_probability:
            # Гол
            self.match_stats[attacking_team]['goals'] += 1
            if attacking_team == 'home':
                self.match.home_score += 1
            else:
                self.match.away_score += 1
            self.match.save()

            self.create_match_event(
                minute,
                'goal',
                agent,
                f"GOAL by {agent.full_name}!"
            )
        else:
            # Блок/промах
            self.create_match_event(
                minute,
                'info',
                agent,
                "Shot blocked by defenders or missed!"
            )


def simulate_one_minute(match_id: int):
    """
    Функция, которую может вызывать Celery периодически.
    """
    try:
        match = Match.objects.get(id=match_id)

        if match.status != 'in_progress':
            logger.info(f"Match {match_id} is not in progress, skipping simulate_one_minute.")
            return

        # Если >=90, завершаем
        if match.current_minute >= 90:
            if match.status != 'finished':
                match.status = 'finished'
                match.save()
            return

        # Запускаем симуляцию 1 минуты
        sim = MatchSimulation(match)
        sim.simulate_minute(match.current_minute + 1)

        # Увеличиваем current_minute
        match.current_minute += 1

        if match.current_minute >= 90:
            match.status = 'finished'
        match.save()

        # Отправляем обновление через WebSocket (если нужно)
        channel_layer = get_channel_layer()
        if channel_layer is not None:
            latest_events = list(match.events.order_by('-minute')[:10].values(
                'minute', 'event_type', 'description'
            ))
            match_data = {
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "status": match.status,
                "events": latest_events
            }
            async_to_sync(channel_layer.group_send)(
                f"match_{match.id}",
                {
                    "type": "match_update",
                    "data": match_data
                }
            )
            logger.info(f"WebSocket update sent for match {match_id}")

    except Exception as e:
        logger.error(f"Error in simulate_one_minute for match {match_id}: {str(e)}")
        raise
