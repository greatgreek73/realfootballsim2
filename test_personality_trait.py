#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match
from matches.personality_engine import PersonalityDecisionEngine
from players.models import Player
from django.conf import settings

def test_trait_detection():
    """Тестирует определение влияющих черт характера"""
    
    print("=== ТЕСТ ОПРЕДЕЛЕНИЯ ЧЕРТ ХАРАКТЕРА ===\n")
    
    print(f"USE_PERSONALITY_ENGINE = {getattr(settings, 'USE_PERSONALITY_ENGINE', False)}\n")
    
    # Получаем активный матч
    match = Match.objects.filter(status='in_progress').first()
    if not match:
        print("Нет активных матчей")
        return
    
    # Берем несколько игроков
    players = Player.objects.filter(
        club__in=[match.home_team_id, match.away_team_id]
    )[:5]
    
    action_types = ['pass', 'shoot', 'dribble', 'tackle', 'long_pass', 'attack']
    
    for player in players:
        print(f"\nИгрок: {player.first_name} {player.last_name}")
        print(f"Черты характера:")
        
        # Показываем все черты игрока
        traits = {
            'aggression': player.aggression,
            'confidence': player.confidence,
            'risk_taking': player.risk_taking,
            'patience': player.patience,
            'teamwork': player.teamwork,
            'leadership': player.leadership,
            'ambition': player.ambition,
            'charisma': player.charisma,
            'endurance': player.endurance,
            'adaptability': player.adaptability
        }
        
        for trait, value in traits.items():
            if value:
                print(f"  {trait}: {value}")
        
        print("\nВлияющие черты для разных действий:")
        for action in action_types:
            trait_name, trait_description = PersonalityDecisionEngine.get_influencing_trait(
                player, action, {}
            )
            if trait_description:
                print(f"  {action}: {trait_description} ({trait_name}={traits.get(trait_name, 0)})")
            else:
                print(f"  {action}: НЕТ ВЛИЯНИЯ")

if __name__ == "__main__":
    test_trait_detection()