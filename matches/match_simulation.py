from django.utils import timezone
from .models import Match, MatchEvent
from .player_agent import PlayerAgent
import random
import logging

logger = logging.getLogger(__name__)

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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

        # Устанавливаем счет в 0, так как матч идет пошагово
        self.match.home_score = self.match.home_score or 0
        self.match.away_score = self.match.away_score or 0
        self.match.save()

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

    def get_random_agent(self, team_type, positions=None):
        agents = list(self.player_agents[team_type].values())
        if positions:
            agents = [agent for agent in agents if any(pos in agent.position for pos in positions)]
        return random.choice(agents) if agents else None

    def set_ball_owner(self, team_type, player_id):
        self.ball_owner = (team_type, player_id)

    def clear_ball_owner(self):
        self.ball_owner = None
        self.current_zone = None

    def assign_ball_to_defender(self, team_type):
        positions_priority = ['Defensive Midfielder', 'Center Back', 'Right Back', 'Left Back', 'Central Midfielder']
        candidates = []
        for pid, agent in self.player_agents[team_type].items():
            if any(pos in agent.position for pos in positions_priority):
                candidates.append(pid)
        if candidates:
            chosen = random.choice(candidates)
            self.set_ball_owner(team_type, chosen)
            self.current_zone = 'defense'
        else:
            all_pids = list(self.player_agents[team_type].keys())
            chosen = random.choice(all_pids)
            self.set_ball_owner(team_type, chosen)
            self.current_zone = 'defense'

    def advance_zone(self, team_type):
        if self.current_zone == 'defense':
            self.current_zone = 'midfield'
        elif self.current_zone == 'midfield':
            self.current_zone = 'attack'

    def _apply_tactics_to_pass(self, team_type, pass_success, intercept_chance):
        tactics = self.match_stats[team_type]['tactics']

        if tactics == 'attacking':
            pass_success = min(1.0, pass_success + 0.1)
            intercept_chance = min(1.0, intercept_chance + 0.1)
        elif tactics == 'defensive':
            pass_success = max(0.0, pass_success - 0.1)
            intercept_chance = min(1.0, intercept_chance + 0.05)
        return pass_success, intercept_chance

    def _apply_tactics_to_shot(self, team_type, shot_chance):
        tactics = self.match_stats[team_type]['tactics']

        if tactics == 'attacking':
            shot_chance = min(1.0, shot_chance + 0.1)
        elif tactics == 'defensive':
            shot_chance = max(0.0, shot_chance - 0.05)
        return shot_chance

    def attempt_pass(self, minute, team_type):
        if not self.ball_owner:
            return False
        owner_team, owner_pid = self.ball_owner
        if owner_team != team_type:
            return False

        passer_agent = self.player_agents[team_type][owner_pid]
        pass_success = min(1.0, (self.match_stats[team_type]['team_midfield']/100)*1.5)

        defending_team = 'away' if team_type == 'home' else 'home'
        defense_factor = self.match_stats[defending_team]['team_defense']
        attack_factor = self.match_stats[team_type]['team_attack']
        intercept_chance = 0.3 if defense_factor > attack_factor else 0.15

        pass_success, intercept_chance = self._apply_tactics_to_pass(team_type, pass_success, intercept_chance)

        if random.random() < intercept_chance:
            self.match_stats[defending_team]['tackles'] += 1
            self.clear_ball_owner()
            self.create_match_event(minute, 'info', None, "Pass intercepted by defenders!")
            return False

        if random.random() < pass_success:
            self.match_stats[team_type]['passes'] += 1
            self.create_match_event(minute, 'info', passer_agent, f"{passer_agent.full_name} passes forward")
            self.advance_zone(team_type)
            new_owner = self.get_random_agent(team_type)
            if new_owner:
                self.set_ball_owner(team_type, new_owner.player_model.id)
            return True
        else:
            self.clear_ball_owner()
            self.create_match_event(minute, 'info', passer_agent, f"{passer_agent.full_name}'s pass goes wide")
            return False

    def attempt_shot(self, minute, team_type):
        if not self.ball_owner:
            return False
        owner_team, owner_pid = self.ball_owner
        if owner_team != team_type:
            return False
            
        shooter = self.player_agents[team_type][owner_pid]
        shot_chance = min(1.0, (self.match_stats[team_type]['team_attack']/100)*1.2)

        shot_chance = self._apply_tactics_to_shot(team_type, shot_chance)

        defending_team = 'away' if team_type == 'home' else 'home'

        if self.match_stats[defending_team]['tactics'] == 'defensive':
            block_chance = 0.6
        else:
            block_chance = 0.5

        if random.random() < block_chance:
            self.match_stats[defending_team]['tackles'] += 1
            self.clear_ball_owner()
            self.create_match_event(minute, 'info', None, "Shot blocked by a defender!")
            return False

        if random.random() < shot_chance:
            self.match_stats[team_type]['goals'] += 1
            self.match_stats[team_type]['shots'] += 1
            if team_type == 'home':
                self.match.home_score += 1
            else:
                self.match.away_score += 1
            self.match.save()

            self.create_match_event(minute, 'goal', shooter, f"GOAL! {shooter.full_name} scores!")
            self.clear_ball_owner()
            return True
        else:
            self.match_stats[team_type]['shots'] += 1
            self.create_match_event(minute, 'info', shooter, f"{shooter.full_name}'s shot goes wide")
            self.clear_ball_owner()
            return False

    def _determine_attacking_team(self):
        home_mid = self.match_stats['home']['team_midfield']
        away_mid = self.match_stats['away']['team_midfield']
        if (home_mid + away_mid) == 0:
            return 'home' if random.random() < 0.5 else 'away'
        home_chance = home_mid / (home_mid + away_mid)
        return 'home' if random.random() < home_chance else 'away'

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

        self.assign_ball_to_defender(attacking_team)

        if self.ball_owner:
            owner_team, owner_pid = self.ball_owner
            owner_agent = self.player_agents[owner_team][owner_pid]
            self.create_match_event(minute, 'info', None, f"Ball currently owned by {owner_team.upper()} player {owner_agent.full_name} in {self.current_zone} zone.")

        if not self.attempt_pass(minute, attacking_team):
            return

        for _ in range(3):
            if not self.ball_owner or self.ball_owner[0] != attacking_team:
                break
            if self.current_zone == 'attack':
                self.attempt_shot(minute, attacking_team)
                break
            else:
                if not self.attempt_pass(minute, attacking_team):
                    break

def simulate_one_minute(match_id: int):
    """
    Симулирует одну игровую минуту для матча.
    Если current_minute < 90, increment и simulate_minute.
    Если достигаем 90, завершаем матч.
    После обновления состояния отправляем данные по WebSocket.
    """
    match = Match.objects.get(id=match_id)
    if match.status == 'in_progress':
        if match.current_minute < 90:
            sim = MatchSimulation(match)
            sim.simulate_minute(match.current_minute + 1)
            match.current_minute += 1
            if match.current_minute >= 90:
                match.status = 'finished'
            match.save()

            # Отправляем обновление по WebSocket
            layer = get_channel_layer()
            data = {
                "minute": match.current_minute,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "events": list(match.events.filter(minute=match.current_minute).values('minute', 'event_type', 'description'))
            }
            async_to_sync(layer.group_send)(
                f"match_{match_id}",
                {
                    "type": "match_update",
                    "data": data
                }
            )
        else:
            # уже 90 минут прошло, ставим finished если нет
            if match.status != 'finished':
                match.status = 'finished'
                match.save()
    else:
        logger.info(f"Match {match_id} is not in progress, skipping simulate_one_minute.")
