#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from matches.personality_engine import PersonalityDecisionEngine
from players.models import Player
from django.conf import settings

def test_personality_system():
    """Полный тест системы personality"""
    
    print("=== ПОЛНЫЙ ТЕСТ СИСТЕМЫ PERSONALITY ===\n")
    
    print(f"USE_PERSONALITY_ENGINE = {getattr(settings, 'USE_PERSONALITY_ENGINE', False)}\n")
    
    # Получаем активный матч
    match = Match.objects.filter(status='in_progress').first()
    if not match:
        match = Match.objects.filter(status='finished').order_by('-id').first()
        if not match:
            print("Нет доступных матчей")
            return
    
    print(f"Используем матч: {match.home_team.name} vs {match.away_team.name}\n")
    
    # Берем игрока с personality_traits
    player = Player.objects.filter(
        club__in=[match.home_team_id, match.away_team_id]
    ).exclude(personality_traits={}).first()
    
    if not player:
        print("Нет игроков с personality_traits")
        return
    
    print(f"Тестируем игрока: {player.first_name} {player.last_name}")
    print(f"personality_traits: {player.personality_traits}\n")
    
    # Тестируем get_influencing_trait для разных действий
    action_types = ['pass', 'shoot', 'dribble', 'tackle', 'long_pass']
    
    print("Результаты get_influencing_trait:")
    for action in action_types:
        trait_name, trait_description = PersonalityDecisionEngine.get_influencing_trait(
            player, action, {}
        )
        trait_value = player.personality_traits.get(trait_name, 0) if trait_name else 0
        print(f"  {action}: {trait_description or 'НЕТ'} (значение: {trait_value})")
    
    # Проверяем последние события с personality_reason
    print("\n\nПоследние события с personality_reason:")
    recent_events = MatchEvent.objects.exclude(
        personality_reason__isnull=True
    ).exclude(
        personality_reason=''
    ).order_by('-id')[:5]
    
    for event in recent_events:
        print(f"\nМинута {event.minute}: {event.event_type}")
        print(f"  Игрок: {event.player.first_name} {event.player.last_name}")
        print(f"  personality_reason: {event.personality_reason}")
        if event.player and event.player.personality_traits:
            print(f"  Черты игрока: {event.player.personality_traits}")

if __name__ == "__main__":
    test_personality_system()