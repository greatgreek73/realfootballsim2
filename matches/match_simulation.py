from django.utils import timezone
from .models import Match, MatchEvent
from .player_agent import PlayerAgent
import random

class MatchSimulation:
    def __init__(self, match):
        self.match = match
        
        # Базовая статистика
        self.match_stats = {
            'home': {'possession': 50, 'shots': 0, 'goals': 0},
            'away': {'possession': 50, 'shots': 0, 'goals': 0}
        }
        
        # Создаем агентов для всех игроков
        self.player_agents = {'home': {}, 'away': {}}
        for team_type in ['home', 'away']:
            team = self.match.home_team if team_type == 'home' else self.match.away_team
            players = team.player_set.all()
            for player in players:
                agent = PlayerAgent(player)
                self.player_agents[team_type][player.id] = agent

    def create_match_event(self, minute, event_type, agent, description):
        """Создание события матча"""
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
        """Получение случайного агента из команды"""
        agents = list(self.player_agents[team_type].values())
        if positions:
            agents = [agent for agent in agents if agent.position in positions]
        return random.choice(agents) if agents else None

    def handle_attack(self, minute, attacking_team, attacker_agent):
        """Обработка атаки"""
        if attacker_agent.perform_action('attack', self.match_stats):
            self.match_stats[attacking_team]['shots'] += 1
            
            if random.random() < 0.3:  # 30% шанс гола
                self.match_stats[attacking_team]['goals'] += 1
                if attacking_team == 'home':
                    self.match.home_score += 1
                else:
                    self.match.away_score += 1
                self.match.save()
                
                self.create_match_event(minute, 'goal', attacker_agent, 
                    f"GOAL! {attacker_agent.full_name} scores!")
            else:
                self.create_match_event(minute, 'miss', attacker_agent,
                    f"{attacker_agent.full_name}'s shot goes wide")

    def simulate_minute(self, minute):
        """Симуляция одной минуты матча"""
        # Определяем атакующую команду
        attacking_team = 'home' if random.random() < 0.5 else 'away'
        
        # Выбираем атакующего игрока
        attacker_agent = self.get_random_agent(attacking_team, 
            ['Center Forward', 'Attacking Midfielder', 'Midfielder'])
            
        if attacker_agent:
            # Получаем решение агента
            action = attacker_agent.decide_action(self.match_stats)
            
            if action == 'attack':
                self.handle_attack(minute, attacking_team, attacker_agent)

    def simulate_match(self):
        """Симуляция всего матча"""
        print("\n=== MATCH START ===\n")
        print(f"Match: {self.match.home_team.name} vs {self.match.away_team.name}")
        
        # Сбрасываем счет
        self.match.home_score = 0
        self.match.away_score = 0
        self.match.status = 'in_progress'
        self.match.save()
        
        # Симуляция матча
        for minute in range(90):
            if minute % 5 == 0:
                print(f"\n=== MINUTE {minute} ===")
                print(f"Score: {self.match.home_score} - {self.match.away_score}")
            
            self.simulate_minute(minute)
            
        # Завершение матча
        self.match.status = 'finished'
        self.match.save()
        
        print("\n=== FINAL STATISTICS ===")
        print(f"Final score: {self.match.home_score} - {self.match.away_score}")
        print(f"Shots: {self.match_stats['home']['shots']} - {self.match_stats['away']['shots']}")

# Функция для запуска симуляции
def simulate_match(match_id: int):
    match = Match.objects.get(id=match_id)
    simulation = MatchSimulation(match)
    simulation.simulate_match()