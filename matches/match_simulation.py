import random
import logging

from django.utils import timezone
from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer
from .models import Match, MatchEvent
from .player_agent import PlayerAgent

# Импорт Celery-задачи (мы напишем её в matches/tasks.py, 
# но здесь уже делаем import, чтобы при вызове simulate_one_minute 
# мы могли запустить задачу на растянутое вещание событий)
#from .tasks import broadcast_minute_events_in_chunks

logger = logging.getLogger(__name__)


class MatchSimulation:
    def __init__(self, match):
        self.match = match
        
        # Инициализация параметров матча
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
                'tactics': 'attacking'
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
                'tactics': 'defensive'
            }
        }

        self.player_agents = {'home': {}, 'away': {}}
        for team_type in ['home', 'away']:
            team = self.match.home_team if team_type == 'home' else self.match.away_team
            players = team.player_set.all()
            for player in players:
                agent = PlayerAgent(player)
                self.player_agents[team_type][player.id] = agent

        self.ball_owner = None
        self.current_zone = None

        self._setup_moments()

    def _calculate_team_parameter(self, team, parameter_type):
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
            else:  # midfield
                if player.position in ['Central Midfielder', 'Defensive Midfielder', 'Attacking Midfielder']:
                    base_value = player.passing + player.vision + player.work_rate
                    weight = 1.5
                else:
                    base_value = player.passing + player.work_rate
                    weight = 1.0

            final_value = base_value * experience_multiplier
            total += final_value * weight
            count += weight

        return round(total / count) if count > 0 else 50

    def create_match_event(self, minute, event_type, agent, description):
        """
        Создает запись о событии в БД (таблица MatchEvent).
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
        Определяем, на каких минутах будет "момент" (попытка атаки) 
        для каждой из команд. Результат - списки self.home_moments_minutes и self.away_moments_minutes.
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

    def simulate_minute(self, minute):
        """
        Проводит логику одного «виртуального» футбольного минуты.
        Создает в БД записи о событиях: 
        - "=============================="
        - "MOMENT at minute..."
        - "Ball owner..."
        - "Goal" или "Shot blocked" и т.д.
        """
        if minute in self.home_moments_minutes:
            attacking_team = 'home'
        elif minute in self.away_moments_minutes:
            attacking_team = 'away'
        else:
            return  # Ничего особенного не произошло в эту минуту

        # Создаем события: начало момента
        self.create_match_event(minute, 'info', None, "==============================")
        self.create_match_event(minute, 'info', None, f"MOMENT at minute {minute}: {attacking_team.upper()} tries to attack!")
        self.create_match_event(minute, 'info', None, "==============================")

        # Определяем, кто владеет мячом
        self.ball_owner = (attacking_team, random.choice(list(self.player_agents[attacking_team].keys())))
        if self.ball_owner:
            owner_team, owner_pid = self.ball_owner
            owner_agent = self.player_agents[owner_team][owner_pid]
            self.create_match_event(
                minute, 
                'info', 
                owner_agent, 
                f"Ball currently owned by {owner_team.upper()} player {owner_agent.full_name}"
            )

        # Попытка забить гол: 30% шанс
        if random.random() < 0.3:
            scorer_agent = self.player_agents[attacking_team][
                random.choice(list(self.player_agents[attacking_team].keys()))
            ]
            self.match_stats[attacking_team]['goals'] += 1

            # Обновляем счет в модели Match
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
            failed_agent = self.player_agents[attacking_team][
                random.choice(list(self.player_agents[attacking_team].keys()))
            ]
            self.create_match_event(
                minute, 
                'info', 
                failed_agent, 
                "Shot blocked by defenders!"
            )


def simulate_one_minute(match_id: int):
    """
    Вызывается каждую "реальную" итерацию (например, Celery 
    раз в 5 секунд), чтобы симулировать 1 мин. игры.
    Но теперь мы УБИРАЕМ прямую отправку событий по WebSocket 
    и вместо этого запускаем задачу broadcast_minute_events_in_chunks,
    которая пошагово отправит события этой минуты.
    """
    try:
        match = Match.objects.get(id=match_id)

        # Не симулируем, если матч не идет
        if match.status != 'in_progress':
            logger.info(f"Match {match_id} is not in progress, skipping simulate_one_minute.")
            return

        # Если 90+ минута - завершаем матч
        if match.current_minute >= 90:
            if match.status != 'finished':
                match.status = 'finished'
                match.save()
            return

        # 1) Симулируем минуту (создает MatchEvent'ы в БД)
        sim = MatchSimulation(match)
        sim.simulate_minute(match.current_minute + 1)

        # Увеличиваем current_minute
        match.current_minute += 1

        # Если дошли до 90 - завершаем
        if match.current_minute >= 90:
            match.status = 'finished'

        match.save()

        # 2) Запускаем Celery-задачу на "поштучную" рассылку
        #    событий этой минуты (match.current_minute) 
        #    за некоторый промежуток (например, 10 секунд).
        from .tasks import broadcast_minute_events_in_chunks
        broadcast_minute_events_in_chunks.delay(
            match_id, 
            match.current_minute, 
            duration=10  # Можно регулировать, например 10с
        )

    except Exception as e:
        logger.error(f"Error in simulate_one_minute for match {match_id}: {str(e)}")
        raise
