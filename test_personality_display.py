#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from players.models import Player
from django.conf import settings
from django.utils import timezone

def add_test_personality_event():
    """Добавляет тестовое событие с personality_reason для проверки отображения"""
    
    print("=== ТЕСТ ОТОБРАЖЕНИЯ PERSONALITY_REASON ===\n")
    
    # Проверяем настройки
    print(f"USE_PERSONALITY_ENGINE = {getattr(settings, 'USE_PERSONALITY_ENGINE', False)}")
    print(f"Порог для отображения черт характера изменен на: 3\n")
    
    # Находим активный или последний матч
    match = Match.objects.filter(status='in_progress').first()
    if not match:
        match = Match.objects.filter(status='finished').order_by('-id').first()
    
    if not match:
        print("Нет доступных матчей!")
        return
    
    print(f"Используем матч: {match.home_team.name} vs {match.away_team.name}")
    print(f"ID матча: {match.id}, Статус: {match.status}\n")
    
    # Находим игрока с personality_traits
    player = Player.objects.filter(
        club__in=[match.home_team_id, match.away_team_id]
    ).exclude(personality_traits={}).first()
    
    if not player:
        print("Нет игроков с personality_traits!")
        return
    
    print(f"Игрок: {player.first_name} {player.last_name}")
    print(f"Черты характера: {player.personality_traits}\n")
    
    # Создаем тестовое событие с personality_reason
    event = MatchEvent.objects.create(
        match=match,
        minute=match.current_minute if match.status == 'in_progress' else 90,
        event_type='test',
        player=player,
        description=f"[ТЕСТ] {player.last_name} выполняет тестовое действие для проверки отображения черт характера",
        personality_reason="Повлияла черта: Уверенность (тестовое событие)"
    )
    
    print(f"[OK] Создано тестовое событие ID={event.id}")
    print(f"   Минута: {event.minute}")
    print(f"   Тип: {event.event_type}")
    print(f"   Описание: {event.description}")
    print(f"   personality_reason: {event.personality_reason}")
    
    # Проверяем последние события с personality_reason
    print("\n\nПоследние 5 событий с personality_reason в этом матче:")
    recent_events = MatchEvent.objects.filter(
        match=match
    ).exclude(
        personality_reason__isnull=True
    ).exclude(
        personality_reason=''
    ).order_by('-id')[:5]
    
    for i, evt in enumerate(recent_events):
        print(f"\n{i+1}. Минута {evt.minute}: {evt.event_type}")
        print(f"   {evt.description[:80]}...")
        print(f"   personality_reason: {evt.personality_reason}")
    
    print(f"\n\n=== ИНСТРУКЦИЯ ДЛЯ ПРОВЕРКИ ===")
    print(f"1. Откройте браузер и перейдите на страницу матча:")
    print(f"   http://localhost:8000/matches/{match.id}/")
    print(f"2. Найдите событие на {event.minute} минуте")
    print(f"3. Под описанием события должна быть строка:")
    print(f"   (Повлияла черта: Уверенность (тестовое событие))")
    print(f"4. Текст должен быть серым, курсивным, маленьким шрифтом")
    
    if match.status == 'in_progress':
        print(f"\n5. Для live-матчей: следите за новыми событиями")
        print(f"   Они должны автоматически появляться с personality_reason")

if __name__ == "__main__":
    add_test_personality_event()