from django.utils import timezone
from .models import Match, MatchEvent
from .player_agent import PlayerAgent
from .pitch import Pitch
import random
import math

class MatchSimulation:
    def __init__(self, match):
        self.match = match
        self.pitch = Pitch()
        self.match_stats = {
            'home': {
                'possession': 50, 
                'shots': 0, 
                'goals': 0,
                'passes': 0,
                'tackles': 0,
                'team_attack': self._calculate_team_parameter(match.home_team, 'attack'),
                'team_defense': self._calculate_team_parameter(match.home_team, 'defense'),
                'team_midfield': self._calculate_team_parameter(match.home_team, 'midfield')
            },
            'away': {
                'possession': 50, 
                'shots': 0, 
                'goals': 0,
                'passes': 0,
                'tackles': 0,
                'team_attack': self._calculate_team_parameter(match.away_team, 'attack'),
                'team_defense': self._calculate_team_parameter(match.away_team, 'defense'),
                'team_midfield': self._calculate_team_parameter(match.away_team, 'midfield')
            }
        }
        
        self.player_agents = {'home': {}, 'away': {}}
        for team_type in ['home', 'away']:
            team = self.match.home_team if team_type == 'home' else self.match.away_team
            players = team.player_set.all()
            for player in players:
                agent = PlayerAgent(player)
                self.player_agents[team_type][player.id] = agent
                
        self.pitch.set_initial_positions(
            list(self.match.home_team.player_set.all()),
            list(self.match.away_team.player_set.all())
        )
        self.pitch.ball_owner = None

    def _calculate_team_parameter(self, team, parameter_type):
        players = team.player_set.all()
        total = 0
        count = 0
        
        for player in players:
            if parameter_type == 'attack':
                if player.position in ['Center Forward', 'Attacking Midfielder']:
                    value = player.finishing + player.heading + player.positioning
                    weight = 1.5
                else:
                    value = player.finishing + player.positioning
                    weight = 1.0
            elif parameter_type == 'defense':
                if player.position in ['Center Back', 'Right Back', 'Left Back', 'Defensive Midfielder']:
                    value = player.marking + player.tackling + player.positioning
                    weight = 1.5
                else:
                    value = player.marking + player.positioning
                    weight = 1.0
            else:  # midfield
                if player.position in ['Central Midfielder', 'Defensive Midfielder', 'Attacking Midfielder']:
                    value = player.passing + player.vision + player.work_rate
                    weight = 1.5
                else:
                    value = player.passing + player.work_rate
                    weight = 1.0
            
            total += value * weight
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
        print(f"{minute}' - {description}")

    def get_random_agent(self, team_type, positions=None):
        agents = list(self.player_agents[team_type].values())
        if positions:
            agents = [agent for agent in agents if agent.position in positions]
        return random.choice(agents) if agents else None

    def update_player_positions(self, minute, attacking_team):
        """Обновляет позиции всех игроков на поле"""
        defending_team = 'away' if attacking_team == 'home' else 'home'
        bx, by = self.pitch.ball_position
        
        # Перемещение атакующей команды
        for (t, pid), (x, y) in list(self.pitch.positions.items()):
            if t != attacking_team:
                continue
                
            agent = self.player_agents[t][pid]
            
            if 'Forward' in agent.position:
                # Нападающие активно двигаются к воротам
                target_x = self.pitch.WIDTH - 20 if t == 'home' else 20
                target_y = self.pitch.HEIGHT // 2 + random.randint(-10, 10)
                dx = 2 if t == 'home' else -2  # Быстрее движутся вперед
                dy = random.randint(-1, 1)
                self.pitch.move_player(t, pid, dx, dy)
                
            elif 'Midfielder' in agent.position:
                # Полузащитники следуют за мячом и поддерживают атаку
                dx = 1 if t == 'home' else -1
                dy = random.randint(-1, 1)
                target_x = bx + 10 if t == 'home' else bx - 10
                target_y = by
                self.pitch.move_player(t, pid, dx, dy)
                
            elif 'Back' in agent.position:
                # Защитники медленно продвигаются вперед
                base_x = self.pitch.WIDTH * 3 // 4 if t == 'home' else self.pitch.WIDTH // 4
                dx = 1 if t == 'home' else -1
                dy = 0
                self.pitch.move_player(t, pid, dx, dy)
        
        # Перемещение обороняющейся команды
        for (t, pid), (x, y) in list(self.pitch.positions.items()):
            if t != defending_team:
                continue
                
            agent = self.player_agents[t][pid]
            
            if 'Back' in agent.position:
                # Защитники отходят к своим воротам
                target_x = 20 if t == 'home' else self.pitch.WIDTH - 20
                dx = -1 if t == 'home' else 1
                dy = random.randint(-1, 1)
                self.pitch.move_player(t, pid, dx, dy)
                
            elif 'Midfielder' in agent.position:
                # Полузащитники прессингуют
                dx = -1 if t == 'home' else 1
                dy = random.randint(-1, 1)
                self.pitch.move_player(t, pid, dx, dy)
                
            else:  # Forward
                # Нападающие отходят назад для прессинга
                dx = -2 if t == 'home' else 2
                dy = random.randint(-1, 1)
                self.pitch.move_player(t, pid, dx, dy)
        
        # Обновляем позицию мяча, если есть владелец
        if self.pitch.ball_owner:
            team_type, player_id = self.pitch.ball_owner
            self.pitch.ball_position = self.pitch.positions[(team_type, player_id)]

    def attempt_pass(self, minute, owner_team, owner_id):
        if not self.pitch.ball_owner:
            return False
            
        x, y = self.pitch.positions[(owner_team, owner_id)]
        teammates = self.pitch.get_nearest_players(x, y, team_type=owner_team)
        teammates = [((t, pid), dist) for ((t, pid), dist) in teammates if pid != owner_id]
        
        if not teammates:
            return False
            
        # Выбираем партнера для паса впереди
        valid_targets = []
        for ((t, pid), dist) in teammates:
            tx, ty = self.pitch.positions[(t, pid)]
            # Проверяем, что партнер находится впереди (для home - правее, для away - левее)
            if (owner_team == 'home' and tx > x) or (owner_team == 'away' and tx < x):
                valid_targets.append(((t, pid), dist))
                
        if valid_targets:
            new_owner, dist = min(valid_targets, key=lambda x: x[1])
        else:
            new_owner, dist = teammates[0]
        
        passer = self.player_agents[owner_team][owner_id]
        pass_success = passer.player_model.passing / 100
        pass_success *= max(0.3, 1 - (dist / self.pitch.WIDTH))
        
        defending_team = 'away' if owner_team == 'home' else 'home'
        interceptors = self.pitch.get_nearest_players(x, y, team_type=defending_team, max_distance=10)
        if interceptors:
            pass_success *= 0.7
            
        if random.random() < pass_success:
            self.pitch.ball_owner = new_owner
            self.pitch.ball_position = self.pitch.positions[new_owner]
            self.match_stats[owner_team]['passes'] += 1
            
            self.create_match_event(minute, 'pass', passer,
                f"{passer.full_name} passes to {self.player_agents[new_owner[0]][new_owner[1]].full_name}")
            return True
        else:
            if interceptors:
                interceptor = interceptors[0][0]
                self.pitch.ball_owner = interceptor
                self.pitch.ball_position = self.pitch.positions[interceptor]
                self.match_stats[defending_team]['tackles'] += 1
                
                self.create_match_event(minute, 'interception', 
                    self.player_agents[interceptor[0]][interceptor[1]],
                    f"{self.player_agents[interceptor[0]][interceptor[1]].full_name} intercepts the pass")
            else:
                self.pitch.ball_owner = None
                self.create_match_event(minute, 'miss', passer,
                    f"{passer.full_name}'s pass goes wide")
            return False

    def attempt_shot(self, minute, team_type, attacker):
        if not attacker or self.pitch.ball_owner != (team_type, attacker.player_model.id):
            return False
            
        chance = attacker.player_model.finishing / 100
        
        x, y = self.pitch.positions[(team_type, attacker.player_model.id)]
        target_x = self.pitch.WIDTH if team_type == 'home' else 0
        distance = abs(x - target_x)
        chance *= max(0.1, 1 - (distance / self.pitch.WIDTH))
        
        defending_team = 'away' if team_type == 'home' else 'home'
        nearest_defenders = self.pitch.get_nearest_players(x, y, defending_team, max_distance=10)
        if nearest_defenders:
            chance *= 0.7
        
        if random.random() < chance:
            self.match_stats[team_type]['goals'] += 1
            self.match_stats[team_type]['shots'] += 1
            if team_type == 'home':
                self.match.home_score += 1
            else:
                self.match.away_score += 1
            self.match.save()
            
            self.create_match_event(minute, 'goal', attacker,
                f"GOAL! {attacker.full_name} scores!")
                
            self.pitch.ball_owner = None
            self.pitch.ball_position = (self.pitch.WIDTH // 2, self.pitch.HEIGHT // 2)
            return True
        else:
            self.match_stats[team_type]['shots'] += 1
            self.create_match_event(minute, 'miss', attacker,
                f"{attacker.full_name}'s shot goes wide")
            self.pitch.ball_owner = None
            return False

    def update_ball_owner(self, attacking_team):
        if not self.pitch.ball_owner:
            bx, by = self.pitch.ball_position
            nearest_players = self.pitch.get_nearest_players(bx, by, team_type=attacking_team)
            if nearest_players:
                self.pitch.ball_owner = nearest_players[0][0]
            
    def simulate_minute(self, minute):
        home_chance = self.match_stats['home']['team_midfield'] / (
            self.match_stats['home']['team_midfield'] + 
            self.match_stats['away']['team_midfield']
        )
        attacking_team = 'home' if random.random() < home_chance else 'away'
        defending_team = 'away' if attacking_team == 'home' else 'home'
        
        # Обновляем позиции игроков
        self.update_player_positions(minute, attacking_team)
        
        # Обновляем владельца мяча
        self.update_ball_owner(attacking_team)
        
        if self.pitch.ball_owner:
            team_type, player_id = self.pitch.ball_owner
            ball_owner = self.player_agents[team_type][player_id]
            x, y = self.pitch.positions[(team_type, player_id)]
            
            target_x = self.pitch.WIDTH if team_type == 'home' else 0
            if abs(x - target_x) < 20:
                self.attempt_shot(minute, team_type, ball_owner)
            else:
                self.attempt_pass(minute, team_type, player_id)

    def simulate_match(self):
        print("\n=== MATCH START ===\n")
        print(f"Match: {self.match.home_team.name} vs {self.match.away_team.name}")
        
        self.match.home_score = 0
        self.match.away_score = 0
        self.match.status = 'in_progress'
        self.match.save()
        
        for minute in range(90):
            if minute % 5 == 0:
                print(f"\n=== MINUTE {minute} ===")
                print(f"Score: {self.match.home_score} - {self.match.away_score}")
            
            self.simulate_minute(minute)
            
        self.match.status = 'finished'
        self.match.save()
        
        print("\n=== FINAL STATISTICS ===")
        print(f"Final score: {self.match.home_score} - {self.match.away_score}")
        print(f"Shots: {self.match_stats['home']['shots']} - {self.match_stats['away']['shots']}")
        print(f"Passes: {self.match_stats['home']['passes']} - {self.match_stats['away']['passes']}")
        print(f"Tackles: {self.match_stats['home']['tackles']} - {self.match_stats['away']['tackles']}")

def simulate_match(match_id: int):
    match = Match.objects.get(id=match_id)
    simulation = MatchSimulation(match)
    simulation.simulate_match()