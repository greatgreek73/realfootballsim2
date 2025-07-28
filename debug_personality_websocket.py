#!/usr/bin/env python
"""
Скрипт для пошаговой отладки передачи personality_reason через WebSocket
"""

import os
import sys
import django
import json

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.serializers.json import DjangoJSONEncoder

def check_personality_reason_flow():
    """Проверяем всю цепочку передачи personality_reason"""
    
    print("=== ОТЛАДКА ПЕРЕДАЧИ PERSONALITY_REASON ===\n")
    
    # 1. Проверяем данные в БД
    print("1. ПРОВЕРКА ДАННЫХ В БД")
    print("-" * 50)
    
    # Находим последний матч
    last_match = Match.objects.filter(status='finished').order_by('-date_played').first()
    if not last_match:
        print("❌ Нет завершенных матчей")
        return
        
    print(f"Последний матч: {last_match.home_team.name} vs {last_match.away_team.name}")
    print(f"ID матча: {last_match.id}")
    
    # Проверяем события с personality_reason
    events_with_pr = MatchEvent.objects.filter(
        match=last_match,
        personality_reason__isnull=False
    ).exclude(personality_reason='')
    
    print(f"\nСобытий с personality_reason: {events_with_pr.count()}")
    
    if events_with_pr.exists():
        print("\nПримеры событий:")
        for event in events_with_pr[:3]:
            print(f"\n  Минута {event.minute}: {event.event_type}")
            print(f"  Описание: {event.description}")
            print(f"  personality_reason: {event.personality_reason}")
    
    # 2. Проверяем формирование данных для WebSocket
    print("\n\n2. ФОРМИРОВАНИЕ ДАННЫХ ДЛЯ WEBSOCKET")
    print("-" * 50)
    
    # Берем первое событие с personality_reason
    test_event = events_with_pr.first()
    if test_event:
        # Эмулируем код из consumers.py
        event_data = {
            'minute': test_event.minute,
            'event_type': test_event.event_type,
            'description': test_event.description,
            'personality_reason': test_event.personality_reason,
            'player_name': test_event.player.last_name if test_event.player else None,
            'related_player_name': test_event.related_player.last_name if test_event.related_player else None,
        }
        
        print("Данные события для WebSocket:")
        print(json.dumps(event_data, indent=2, ensure_ascii=False))
        
        # 3. Проверяем формирование полного сообщения
        print("\n\n3. ФОРМИРОВАНИЕ ПОЛНОГО СООБЩЕНИЯ")
        print("-" * 50)
        
        message_payload = {
            "type": "match_update",
            "data": {
                "match_id": str(last_match.id),
                "minute": test_event.minute,
                "home_score": last_match.home_score,
                "away_score": last_match.away_score,
                "status": last_match.status,
                "events": [event_data],
                "partial_update": True,
            }
        }
        
        print("Полное сообщение для WebSocket:")
        print(json.dumps(message_payload, indent=2, ensure_ascii=False, cls=DjangoJSONEncoder))
        
        # 4. Проверяем channel layer
        print("\n\n4. ПРОВЕРКА CHANNEL LAYER")
        print("-" * 50)
        
        channel_layer = get_channel_layer()
        if channel_layer:
            print("✅ Channel layer доступен")
            print(f"Тип: {type(channel_layer)}")
            
            # Попробуем отправить тестовое сообщение
            try:
                group_name = f"match_{last_match.id}"
                print(f"\nОтправка в группу: {group_name}")
                
                # Это не отправит реальное сообщение, если нет активных подключений
                # но проверит, что механизм работает
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    message_payload
                )
                print("✅ Сообщение отправлено (или нет активных подключений)")
            except Exception as e:
                print(f"❌ Ошибка отправки: {e}")
        else:
            print("❌ Channel layer недоступен")
    
    # 5. JavaScript обработка
    print("\n\n5. JAVASCRIPT ОБРАБОТКА (см. консоль браузера)")
    print("-" * 50)
    print("В консоли браузера должны появиться сообщения:")
    print("  - WS data: {...}")
    print("  - === DEBUG: WebSocket Events ===")
    print("  - Event 0: {...}")
    print("  - Event 0 has personality_reason: ...")
    print("  - === DEBUG: addEventToList ===")
    print("  - Personality reason: ...")
    print("  - DEBUG: Adding personality_reason to HTML: ...")
    
    print("\n\n6. ИТОГОВАЯ ПРОВЕРКА")
    print("-" * 50)
    print("Откройте страницу матча и проверьте:")
    print("1. Консоль браузера (F12) - должны быть отладочные сообщения")
    print("2. HTML события должен содержать <div class='personality-reason'>")
    print("3. Текст personality_reason должен отображаться курсивом под событием")
    
    print("\n\n7. ТЕСТОВАЯ СТРАНИЦА")
    print("-" * 50)
    print("Откройте в браузере: /test_personality_reason_display.html")
    print("Эта страница эмулирует отображение событий с personality_reason")

if __name__ == "__main__":
    check_personality_reason_flow()