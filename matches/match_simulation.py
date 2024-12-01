from typing import Dict, List, Tuple
from django.db import models
from django.utils import timezone
from .models import Match, MatchEvent
from matches.match_preparation import PreMatchPreparation
import random
import logging

logger = logging.getLogger('matches')

class MatchSimulation:
    """Основной движок симуляции матча"""
    
    # Временные периоды матча
    PERIODS = [
        (0, 15),    # Начало матча
        (15, 30),   # Первый тайм
        (30, 45),   # Конец первого тайма
        (45, 60),   # Начало второго тайма
        (60, 75),   # Второй тайм
        (75, 90),   # Концовка матча
    ]
    
    # Обновленные модификаторы событий
    PERIOD_MODIFIERS = {
        0: {'attack_chance': 0.6, 'goal_chance': 0.4, 'fatigue_rate': 0.5},
        1: {'attack_chance': 0.8, 'goal_chance': 0.5, 'fatigue_rate': 0.8},
        2: {'attack_chance': 0.9, 'goal_chance': 0.6, 'fatigue_rate': 1.0},
        3: {'attack_chance': 0.7, 'goal_chance': 0.5, 'fatigue_rate': 0.7},
        4: {'attack_chance': 0.8, 'goal_chance': 0.6, 'fatigue_rate': 1.1},
        5: {'attack_chance': 1.0, 'goal_chance': 0.7, 'fatigue_rate': 1.2}
    }

    def __init__(self, match):
        self.match = match
        self.preparation = PreMatchPreparation(match)
        
        if not self.preparation.prepare_match():
            raise ValueError("Ошибка подготовки матча")
            
        self.match_stats = {
            'home': {'possession': 50, 'shots': 0, 'shots_on_target': 0, 'corners': 0,
                    'fouls': 0, 'attacks': 0, 'dangerous_attacks': 0},
            'away': {'possession': 50, 'shots': 0, 'shots_on_target': 0, 'corners': 0,
                    'fouls': 0, 'attacks': 0, 'dangerous_attacks': 0}
        }
        
        self.match_parameters = self.preparation.match_parameters
        self.last_event_minute = -1  # Для контроля частоты событий

    def get_period_index(self, minute):
        for i, (start, end) in enumerate(self.PERIODS):
            if start <= minute < end:
                return i
        return 5

    def create_match_event(self, minute, event_type, player, description):
        MatchEvent.objects.create(
            match=self.match,
            minute=minute,
            event_type=event_type,
            player=player,
            description=description
        )
        print(f"{minute}' - {description}")

    def get_random_player(self, team_type, positions=None):
        team = self.match.home_team if team_type == 'home' else self.match.away_team
        players = team.player_set.all()
        if positions:
            players = players.filter(position__in=positions)
        return random.choice(players) if players.exists() else None

    def update_player_condition(self, team_type, player_id, minute):
        player_condition = self.match_parameters[team_type]['players_condition'][player_id]
        period_index = self.get_period_index(minute)
        fatigue_rate = self.PERIOD_MODIFIERS[period_index]['fatigue_rate']
        
        player = self.match.home_team.player_set.get(id=player_id) if team_type == 'home' \
            else self.match.away_team.player_set.get(id=player_id)
        
        stamina_factor = player.stamina / 100
        new_condition = player_condition - (1 - stamina_factor) * fatigue_rate
        self.match_parameters[team_type]['players_condition'][player_id] = max(0, new_condition)

    def calculate_attack_success(self, attacking_team, minute):
        defending_team = 'away' if attacking_team == 'home' else 'home'
        period_index = self.get_period_index(minute)
        
        attack_power = self.match_parameters[attacking_team]['team_attack']
        defense_power = self.match_parameters[defending_team]['team_defense']
        midfield_power = self.match_parameters[attacking_team]['team_midfield']
        
        attack_condition = sum(self.match_parameters[attacking_team]['players_condition'].values()) / 11
        defense_condition = sum(self.match_parameters[defending_team]['players_condition'].values()) / 11
        
        attack_power *= (attack_condition / 100)
        defense_power *= (defense_condition / 100)
        
        base_chance = (attack_power + midfield_power/2) / (defense_power + 50)
        period_modifier = self.PERIOD_MODIFIERS[period_index]['attack_chance']
        
        return min(0.9, base_chance * period_modifier)

    def simulate_minute(self, minute):
        if minute - self.last_event_minute < 2:
            return

        period_index = self.get_period_index(minute)
        modifiers = self.PERIOD_MODIFIERS[period_index]
        
        for team_type in ['home', 'away']:
            for player_id in self.match_parameters[team_type]['players_condition'].keys():
                self.update_player_condition(team_type, player_id, minute)
        
        home_mid = self.match_parameters['home']['team_midfield']
        away_mid = self.match_parameters['away']['team_midfield']
        total_mid = home_mid + away_mid
        
        self.match_stats['home']['possession'] = round((home_mid / total_mid) * 100)
        self.match_stats['away']['possession'] = 100 - self.match_stats['home']['possession']
        
        attacking_team = 'home' if random.random() < (self.match_stats['home']['possession'] / 100) else 'away'
        defending_team = 'away' if attacking_team == 'home' else 'home'
            
        if minute % 5 == 0:
            attacking_team_name = "Home team" if attacking_team == 'home' else "Away team"
            print(f"{attacking_team_name} attacking!")
        
        attack_chance = self.calculate_attack_success(attacking_team, minute)
        if random.random() < attack_chance * modifiers['attack_chance']:
            self.match_stats[attacking_team]['attacks'] += 1
            
            attacker = self.get_random_player(attacking_team, ['Center Forward', 'Attacking Midfielder', 'Midfielder'])
            if attacker:
                self.create_match_event(minute, 'attack_start', attacker, f"{attacker.full_name} starts the attack")
            
            shot_chance = attack_chance * modifiers['goal_chance']
            if random.random() < shot_chance:
                self.match_stats[attacking_team]['dangerous_attacks'] += 1
                self.match_stats[attacking_team]['shots'] += 1
                
                outcome = random.random()
                
                if outcome < 0.3:  # 30% - защитник блокирует
                    defender = self.get_random_player(defending_team, ['Center Back', 'Full Back'])
                    if defender:
                        self.create_match_event(minute, 'defense', defender, 
                            f"{defender.full_name} makes a great defensive play")
                
                elif outcome < 0.6:  # 30% - удар мимо
                    shooter = self.get_random_player(attacking_team, ['Center Forward', 'Attacking Midfielder'])
                    if shooter:
                        self.create_match_event(minute, 'miss', shooter, f"{shooter.full_name}'s shot goes wide")
                        if random.random() < 0.4:
                            self.match_stats[attacking_team]['corners'] += 1
                            self.create_match_event(minute, 'corner', None, "Corner kick")
                
                elif outcome < 0.85:  # 25% - сейв вратаря
                    goalkeeper = self.get_random_player(defending_team, ['Goalkeeper'])
                    self.match_stats[attacking_team]['shots_on_target'] += 1
                    if goalkeeper:
                        self.create_match_event(minute, 'save', goalkeeper, 
                            f"Great save by {goalkeeper.full_name}!")
                
                else:  # 15% - гол
                    self.match_stats[attacking_team]['shots_on_target'] += 1
                    scorer = self.get_random_player(attacking_team, ['Center Forward', 'Attacking Midfielder'])
                    if scorer:
                        self.create_match_event(minute, 'goal', scorer, f"GOAL! {scorer.full_name} scores!")
                        if attacking_team == 'home':
                            self.match.home_score += 1
                        else:
                            self.match.away_score += 1
                        self.match.save()
            
            self.last_event_minute = minute
        
        if random.random() < 0.05 * modifiers['fatigue_rate']:
            fouler = self.get_random_player(defending_team)
            victim = self.get_random_player(attacking_team)
            if fouler and victim:
                self.match_stats[defending_team]['fouls'] += 1
                self.create_match_event(minute, 'foul', fouler, 
                    f"Foul by {fouler.full_name} on {victim.full_name}")
                self.last_event_minute = minute

    def simulate_match(self):
        print("\n=== MATCH START ===\n")
        
        self.match.status = 'in_progress'
        self.match.save()
        
        for minute in range(90):
            if minute % 5 == 0:
                print(f"\n=== MINUTE {minute} ===")
                print(f"Score: {self.match.home_score} - {self.match.away_score}")
                if minute > 0:
                    print(f"Possession: {self.match_stats['home']['possession']}% - {self.match_stats['away']['possession']}%")
                    print(f"Shots (on target): {self.match_stats['home']['shots']} ({self.match_stats['home']['shots_on_target']}) - "
                          f"{self.match_stats['away']['shots']} ({self.match_stats['away']['shots_on_target']})")
            self.simulate_minute(minute)
            
        self.match.status = 'finished'
        self.match.save()
        
        print("\n=== FINAL STATISTICS ===\n")
        print(f"Final score: {self.match.home_score} - {self.match.away_score}\n")
        
        print("Home team statistics:")
        print(f"Possession: {self.match_stats['home']['possession']}%")
        print(f"Shots (on target): {self.match_stats['home']['shots']} ({self.match_stats['home']['shots_on_target']})")
        print(f"Corners: {self.match_stats['home']['corners']}")
        print(f"Fouls: {self.match_stats['home']['fouls']}")
        print(f"Attacks (dangerous): {self.match_stats['home']['attacks']} ({self.match_stats['home']['dangerous_attacks']})")
        
        print("\nAway team statistics:")
        print(f"Possession: {self.match_stats['away']['possession']}%")
        print(f"Shots (on target): {self.match_stats['away']['shots']} ({self.match_stats['away']['shots_on_target']})")
        print(f"Corners: {self.match_stats['away']['corners']}")
        print(f"Fouls: {self.match_stats['away']['fouls']}")
        print(f"Attacks (dangerous): {self.match_stats['away']['attacks']} ({self.match_stats['away']['dangerous_attacks']})")


def simulate_match(match_id: int):
    """
    Функция для обратной совместимости со старым кодом
    
    Args:
        match_id: int - ID матча для симуляции
    """
    match = Match.objects.get(id=match_id)
    simulation = MatchSimulation(match)
    simulation.simulate_match()