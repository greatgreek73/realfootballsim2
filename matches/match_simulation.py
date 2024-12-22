from django.utils import timezone
from .models import Match, MatchEvent
from .player_agent import PlayerAgent
import random
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
        player_model = agent.player_model if agent else None
        MatchEvent.objects.create(
            match=self.match,
            minute=minute,
            event_type=event_type,
            player=player_model,
            description=description
        )

    def _setup_moments(self):
        base_min, base_max = 10, 20
        home_strength = (self.match_stats['home']['team_attack'] + self.match_stats['home']['team_midfield']) / 2
        away_strength = (self.match_stats['away']['team_attack'] + self.match_stats['away']['team_midfield']) / 2
        
        home_factor = min(home_strength / 100, 1.0)
        away_factor = min(away_strength / 100, 1.0)
        
        home_chances = int(base_min + (base_max - base_min)*home_factor)
        away_chances = int(base_min + (base_max - base_min)*away_factor)

        all_minutes = list(range(1, 90))
        random.shuffle(all_minutes)

        self.home_moments_minutes = sorted(all_minutes[:home_chances])
        self.away_moments_minutes = sorted(all_minutes[home_chances:home_chances+away_chances])

    def simulate_minute(self, minute):
        # Симуляция одной минуты матча
        if minute in self.home_moments_minutes:
            attacking_team = 'home'
        elif minute in self.away_moments_minutes:
            attacking_team = 'away'
        else:
            return

        self.create_match_event(minute, 'info', None, "==============================")
        self.create_match_event(minute, 'info', None, f"MOMENT at minute {minute}: {attacking_team.upper()} tries to attack!")
        self.create_match_event(minute, 'info', None, "==============================")

        self.ball_owner = (attacking_team, random.choice(list(self.player_agents[attacking_team].keys())))

        if self.ball_owner:
            owner_team, owner_pid = self.ball_owner
            owner_agent = self.player_agents[owner_team][owner_pid]
            self.create_match_event(minute, 'info', owner_agent, f"Ball currently owned by {owner_team.upper()} player {owner_agent.full_name}")

        # Симуляция атаки
        if random.random() < 0.3:  # 30% шанс забить гол
            scorer_agent = self.player_agents[attacking_team][random.choice(list(self.player_agents[attacking_team].keys()))]
            self.match_stats[attacking_team]['goals'] += 1
            if attacking_team == 'home':
                self.match.home_score += 1
            else:
                self.match.away_score += 1
            self.match.save()
            self.create_match_event(minute, 'goal', scorer_agent, f"GOAL! {scorer_agent.full_name} scores!")
        else:
            failed_agent = self.player_agents[attacking_team][random.choice(list(self.player_agents[attacking_team].keys()))]
            self.create_match_event(minute, 'info', failed_agent, "Shot blocked by defenders!")


def simulate_one_minute(match_id: int):
    """
    Симулирует одну игровую минуту для матча.
    """
    try:
        match = Match.objects.get(id=match_id)
        
        if match.status != 'in_progress':
            logger.info(f"Match {match_id} is not in progress, skipping simulate_one_minute.")
            return
            
        if match.current_minute >= 90:
            if match.status != 'finished':
                match.status = 'finished'
                match.save()
            return

        # Симуляция минуты
        sim = MatchSimulation(match)
        sim.simulate_minute(match.current_minute + 1)
        match.current_minute += 1
        
        # Проверяем окончание матча
        if match.current_minute >= 90:
            match.status = 'finished'
        match.save()

        # Подготовка данных для отправки
        try:
            # Получаем события этой минуты
            new_events = list(match.events.filter(
                minute=match.current_minute
            ).values('minute', 'event_type', 'description'))

            # Подготавливаем данные для отправки
            update_data = {
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "status": match.status,
                "events": new_events
            }
            logger.debug(f"Prepared update data for match {match_id}: {update_data}")

            # Отправляем через WebSocket
            channel_layer = get_channel_layer()
            logger.info(f"Sending update to match_{match_id} group")
            
            async_to_sync(channel_layer.group_send)(
                f"match_{match_id}",
                {
                    "type": "match_update",
                    "data": update_data
                }
            )
            logger.info(f"Successfully sent update to match_{match_id} group")
            
        except Exception as e:
            logger.error(f"Error sending WebSocket update for match {match_id}: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Error in simulate_one_minute for match {match_id}: {str(e)}")
        raise