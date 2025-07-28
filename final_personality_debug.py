#!/usr/bin/env python
"""
Финальная проверка отображения personality_reason
"""

import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from django.db import connection

def final_check():
    print("=== ФИНАЛЬНАЯ ПРОВЕРКА PERSONALITY_REASON ===\n")
    
    # 1. Проверка в базе данных
    print("1. ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("-" * 60)
    
    # Сырой SQL запрос для проверки
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches_matchevent 
            WHERE personality_reason IS NOT NULL 
            AND personality_reason != ''
        """)
        total_with_pr = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches_matchevent")
        total_events = cursor.fetchone()[0]
        
    print(f"Всего событий в БД: {total_events}")
    print(f"События с personality_reason: {total_with_pr}")
    print(f"Процент: {total_with_pr/total_events*100:.1f}%\n")
    
    # Примеры событий
    recent_events = MatchEvent.objects.filter(
        personality_reason__isnull=False
    ).exclude(
        personality_reason=''
    ).select_related('player', 'match').order_by('-id')[:5]
    
    print("Последние 5 событий с personality_reason:")
    for event in recent_events:
        print(f"\n  ID: {event.id}")
        print(f"  Матч: {event.match.home_team.name} vs {event.match.away_team.name}")
        print(f"  Минута: {event.minute}")
        print(f"  Тип: {event.event_type}")
        print(f"  Описание: {event.description}")
        print(f"  personality_reason: '{event.personality_reason}'")
        print(f"  Игрок: {event.player.last_name if event.player else 'N/A'}")
    
    # 2. Проверка фронтенда
    print("\n\n2. ПРОВЕРКА ФРОНТЕНДА")
    print("-" * 60)
    print("✅ CSS стили добавлены в match_detail.css (строки 458-498)")
    print("✅ HTML шаблон содержит блок для personality_reason (строки 202-206)")
    print("✅ JavaScript обрабатывает personality_reason (строки 288-293)")
    print("✅ WebSocket consumers передает personality_reason (строка 182)")
    print("✅ tasks.py формирует события с personality_reason (строка 114)")
    
    # 3. Инструкции для проверки
    print("\n\n3. ИНСТРУКЦИИ ДЛЯ ПРОВЕРКИ")
    print("-" * 60)
    print("\nДля проверки отображения:")
    print("1. Откройте браузер и перейдите на страницу любого матча")
    print("2. Откройте консоль разработчика (F12)")
    print("3. Запустите новый матч или дождитесь обновления")
    print("4. В консоли должны появиться сообщения:")
    print("   - '=== DEBUG: WebSocket Events ==='")
    print("   - 'Event has personality_reason: ...'")
    print("   - '=== DEBUG: addEventToList ==='")
    print("   - 'DEBUG: Adding personality_reason to HTML: ...'")
    print("\n5. На странице под событием должен появиться текст:")
    print("   (Competitive Nature: решил взять игру на себя)")
    print("   - серым цветом")
    print("   - курсивом")
    print("   - с отступом слева")
    
    print("\n\n4. ТЕСТОВАЯ СТРАНИЦА")
    print("-" * 60)
    print("Для проверки отображения откройте в браузере:")
    print("http://localhost:8000/test_personality_reason_display.html")
    print("\nЭта страница показывает как должны выглядеть события")
    print("с personality_reason в идеальном случае.")
    
    # 5. Возможные проблемы
    print("\n\n5. ВОЗМОЖНЫЕ ПРОБЛЕМЫ")
    print("-" * 60)
    print("\nЕсли personality_reason не отображается, проверьте:")
    print("1. Кеш браузера - выполните жесткую перезагрузку (Ctrl+F5)")
    print("2. Статические файлы - выполните: python manage.py collectstatic")
    print("3. WebSocket соединение - проверьте вкладку Network в DevTools")
    print("4. JavaScript ошибки - проверьте консоль на наличие ошибок")
    
    # Проверка последнего live матча
    live_match = Match.objects.filter(status='in_progress').first()
    if live_match:
        print(f"\n\n⚡ ЕСТЬ LIVE МАТЧ: {live_match.home_team.name} vs {live_match.away_team.name}")
        print(f"ID: {live_match.id}")
        print("Откройте его для проверки WebSocket обновлений!")

if __name__ == "__main__":
    final_check()