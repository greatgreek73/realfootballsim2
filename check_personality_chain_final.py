#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from django.conf import settings

def check_personality_chain():
    """Финальная проверка всей цепочки personality_reason"""
    
    print("=== ФИНАЛЬНАЯ ПРОВЕРКА PERSONALITY_REASON ===\n")
    
    # 1. Проверяем настройки
    print("1. НАСТРОЙКИ:")
    print(f"   USE_PERSONALITY_ENGINE = {getattr(settings, 'USE_PERSONALITY_ENGINE', False)}")
    print(f"   Порог для черт характера = 3")
    
    # 2. Проверяем последние события в БД
    print("\n2. ПОСЛЕДНИЕ СОБЫТИЯ В БД С PERSONALITY_REASON:")
    events = MatchEvent.objects.exclude(
        personality_reason__isnull=True
    ).exclude(
        personality_reason=''
    ).order_by('-id')[:3]
    
    for event in events:
        print(f"\n   Событие ID={event.id}, Матч ID={event.match_id}")
        print(f"   Минута: {event.minute}, Тип: {event.event_type}")
        print(f"   personality_reason: '{event.personality_reason}'")
        
        # Проверяем как это событие будет выглядеть в JSON для WebSocket
        event_json = {
            'minute': event.minute,
            'event_type': event.event_type,
            'description': event.description,
            'personality_reason': event.personality_reason,
            'player_name': f"{event.player.first_name} {event.player.last_name}" if event.player else None,
            'related_player_name': f"{event.related_player.first_name} {event.related_player.last_name}" if event.related_player else None
        }
        
        print(f"   JSON для WebSocket:")
        print(f"   {json.dumps(event_json, ensure_ascii=False, indent=6)}")
    
    # 3. Проверяем JavaScript
    print("\n3. JAVASCRIPT ОБРАБОТКА:")
    print("   В live_match.js добавлены отладочные console.log:")
    print("   - При получении WebSocket сообщения")
    print("   - При обработке каждого события")
    print("   - Специальная проверка personality_reason")
    
    # 4. Итоговая инструкция
    print("\n4. ИНСТРУКЦИЯ ДЛЯ ПРОВЕРКИ:")
    print("   a) Очистите кэш браузера (Ctrl+Shift+Delete или Ctrl+F5)")
    print("   b) Откройте консоль разработчика (F12)")
    print("   c) Откройте страницу любого активного матча")
    print("   d) В консоли должны появиться сообщения:")
    print("      - 'WebSocket message received:' с полными данными")
    print("      - 'Processing event:' для каждого события")
    print("      - 'Event has personality_reason:' если есть personality_reason")
    print("   e) На странице под событиями должен появиться серый курсивный текст")
    
    # 5. Проверка статических файлов
    static_js_path = os.path.join(settings.STATIC_ROOT, 'matches', 'js', 'live_match.js')
    if os.path.exists(static_js_path):
        with open(static_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'console.log("Event has personality_reason:"' in content:
                print("\n5. СТАТИЧЕСКИЕ ФАЙЛЫ:")
                print("   [OK] Отладочный код присутствует в статических файлах")
            else:
                print("\n5. СТАТИЧЕСКИЕ ФАЙЛЫ:")
                print("   [ВНИМАНИЕ] Отладочный код НЕ найден в статических файлах")
                print("   Выполните: python manage.py collectstatic --noinput")

if __name__ == "__main__":
    check_personality_chain()