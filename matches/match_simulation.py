import random
import logging

from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Match, MatchEvent
from .player_agent import PlayerAgent
from players.models import Player

logger = logging.getLogger(__name__)


class MatchSimulation:
    def __init__(self, match: Match):
        self.match = match

        # Инициализация «статов» матча для home/away
        self.match_stats = {
            'home': {
                'possession': 50,
                'shots': 0,
                'goals': 0,
                'passes': 0,
                'tackles': 0,
                'team_attack': self._calculate_team_parameter(match.home_team, 'attack'),
                'team_defense': self._calculate_team_parameter(match.home_team, 'defense'),
                'team_midfield': self._calculate_team_parameter(match.home_team, 'midfield'),
                'tactics': 'attacking',
            },
            'away': {
                'possession': 50,
                'shots': 0,
                'goals': 0,
                'passes': 0,
                'tackles': 0,
                'team_attack': self._calculate_team_parameter(match.away_team, 'attack'),
                'team_defense': self._calculate_team_parameter(match.away_team, 'defense'),
                'team_midfield': self._calculate_team_parameter(match.away_team, 'midfield'),
                'tactics': 'defensive',
            },
        }

        # Создадим словарь "агентов" игроков
        self.player_agents = {
            'home': {},
            'away': {}
        }

        # Получаем ID игроков из составов
        home_lineup_ids = []
        away_lineup_ids = []

        if self.match.home_lineup and isinstance(self.match.home_lineup, dict):
            # Проверяем, есть ли вложенный словарь "lineup"
            if "lineup" in self.match.home_lineup:
                home_lineup = self.match.home_lineup["lineup"]
            else:
                home_lineup = self.match.home_lineup
            # Берём только значения (ID игроков)
            home_lineup_ids = list(map(str, home_lineup.values()))

        if self.match.away_lineup and isinstance(self.match.away_lineup, dict):
            # То же самое для away_lineup
            if "lineup" in self.match.away_lineup:
                away_lineup = self.match.away_lineup["lineup"]
            else:
                away_lineup = self.match.away_lineup
            away_lineup_ids = list(map(str, away_lineup.values()))

        logger.info(f"Home lineup IDs: {home_lineup_ids}")
        logger.info(f"Away lineup IDs: {away_lineup_ids}")

        # Получаем объекты игроков по их ID
        home_players = Player.objects.filter(pk__in=home_lineup_ids)
        away_players = Player.objects.filter(pk__in=away_lineup_ids)

        # Создаем агентов для каждого игрока
        for player in home_players:
            agent = PlayerAgent(player)
            self.player_agents['home'][player.id] = agent

        for player in away_players:
            agent = PlayerAgent(player)
            self.player_agents['away'][player.id] = agent

        # Изначально "владелец мяча" и "зона" не заданы
        self.ball_owner = None
        self.current_zone = None

        # Подготовим списки минут, когда возникают опасные моменты
        self._setup_moments()

    def _calculate_team_parameter(self, team, parameter_type):
        """
        Примерная функция, которая усредняет характеристики команды
        """
        players = team.player_set.all()
        total = 0
        count = 0

        for player in players:
            experience_multiplier = 1 + player.experience * 0.01

            if parameter_type == 'attack':
                if player.position in ['Center Forward', 'Attacking Midfielder']:
                    base_value = player.finishing + player.heading + player.long_range
                    weight = 1.5
                else:
                    base_value = player.finishing + player.long_range
                    weight = 1.0

            elif parameter_type == 'defense':
                if player.position in ['Center Back', 'Right Back', 'Left Back', 'Defensive Midfielder']:
                    base_value = player.marking + player.tackling + player.heading
                    weight = 1.5
                else:
                    base_value = player.marking + player.tackling
                    weight = 1.0

            else:  # "midfield"
                if player.position in ['Central Midfielder', 'Defensive Midfielder', 'Attacking Midfielder']:
                    base_value = player.passing + player.vision + player.work_rate
                    weight = 1.5
                else:
                    base_value = player.passing + player.work_rate
                    weight = 1.0

            final_value = base_value * experience_multiplier
            total += (final_value * weight)
            count += weight

        if count > 0:
            return round(total / count)
        else:
            return 50

    def create_match_event(self, minute, event_type, agent, description):
        """
        Создаём MatchEvent в БД (запись о событии).
        agent.player_model — ссылка на Player
        """
        player_model = agent.player_model if agent else None
        MatchEvent.objects.create(
            match=self.match,
            minute=minute,
            event_type=event_type,
            player=player_model,
            description=description
        )

    def _setup_moments(self):
        """
        Определяем, на каких минутах будет "опасный момент/атака" 
        у home / away.
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
        self.away_moments_minutes = sorted(all_minutes[home_chances:home_chances + away_chances])

    def simulate_minute(self, minute):
        """
        Логика "1 минута матча": создаём MatchEvent'ы (гол, блок и т. д.).
        """
        if minute in self.home_moments_minutes:
            attacking_team = 'home'
        elif minute in self.away_moments_minutes:
            attacking_team = 'away'
        else:
            return  # Ничего не произошло

        # События
        self.create_match_event(minute, 'info', None, "==============================")
        self.create_match_event(minute, 'info', None, f"MOMENT at minute {minute}: {attacking_team.upper()} tries to attack!")
        self.create_match_event(minute, 'info', None, "==============================")

        # Выбираем рандомного игрока из того, что у нас есть в self.player_agents
        if not self.player_agents[attacking_team]:
            # Если вдруг lineup пуст
            logger.warning(f"No players in {attacking_team} lineup to simulate minute {minute}.")
            return

        random_player_id = random.choice(list(self.player_agents[attacking_team].keys()))
        owner_agent = self.player_agents[attacking_team][random_player_id]

        self.create_match_event(
            minute,
            'info',
            owner_agent,
            f"Ball currently owned by {attacking_team.upper()} player {owner_agent.full_name}"
        )

        # 30% шанс гола
        if random.random() < 0.3:
            # Случайный "автор гола"
            scorer_player_id = random.choice(list(self.player_agents[attacking_team].keys()))
            scorer_agent = self.player_agents[attacking_team][scorer_player_id]

            self.match_stats[attacking_team]['goals'] += 1
            if attacking_team == 'home':
                self.match.home_score += 1
            else:
                self.match.away_score += 1
            self.match.save()

            self.create_match_event(
                minute,
                'goal',
                scorer_agent,
                f"GOAL! {scorer_agent.full_name} scores!"
            )
        else:
            # "Shot blocked"
            self.create_match_event(
                minute,
                'info',
                owner_agent,
                "Shot blocked by defenders!"
            )


def simulate_one_minute(match_id: int):
    """
    Функция, которую может вызывать Celery (каждые 5 секунд и т. д.).
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

        # Отправляем обновление через WebSocket
        channel_layer = get_channel_layer()
        if channel_layer is not None:
            # Получаем последние события матча
            latest_events = list(match.events.order_by('-minute')[:10].values(
                'minute', 'event_type', 'description'
            ))
            
            # Формируем данные для отправки
            match_data = {
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "status": match.status,
                "events": latest_events
            }
            
            # Отправляем в группу WebSocket
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