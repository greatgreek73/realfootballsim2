#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from matches.match_simulation import simulate_one_action
from django.conf import settings
import json

def test_personality_chain():
    """Тестирует всю цепочку передачи personality_reason"""
    
    print("=== ОТЛАДКА PERSONALITY_REASON ===\n")
    
    # Шаг 1: Проверяем настройки
    print("ШАГ 1: Проверка настроек")
    print(f"USE_PERSONALITY_ENGINE = {getattr(settings, 'USE_PERSONALITY_ENGINE', False)}")
    print()
    
    # Шаг 2: Получаем активный матч для тестирования
    print("ШАГ 2: Поиск активного матча")
    active_match = Match.objects.filter(status='in_progress').first()
    if not active_match:
        print("Нет активных матчей. Ищем последний завершенный...")
        active_match = Match.objects.filter(status='finished').order_by('-id').first()
    
    if not active_match:
        print("ОШИБКА: Нет матчей для тестирования!")
        return
    
    print(f"Используем матч ID={active_match.id}: {active_match.home_team.name} vs {active_match.away_team.name}")
    print()
    
    # Шаг 3: Выполняем simulate_one_action
    print("ШАГ 3: Выполнение simulate_one_action")
    try:
        result = simulate_one_action(active_match)
        print("Результат simulate_one_action:")
        print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
        
        # Проверяем наличие personality_reason в событии
        if result.get('event'):
            event_data = result['event']
            print(f"\nСобытие содержит personality_reason: {'ДА' if event_data.get('personality_reason') else 'НЕТ'}")
            if event_data.get('personality_reason'):
                print(f"Значение: {event_data['personality_reason']}")
        print()
    except Exception as e:
        print(f"ОШИБКА при выполнении simulate_one_action: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Шаг 4: Проверяем последние события в БД
    print("ШАГ 4: Проверка последних событий в БД")
    recent_events = MatchEvent.objects.filter(match=active_match).order_by('-id')[:5]
    
    if recent_events:
        print(f"Последние {len(recent_events)} событий матча:")
        for i, event in enumerate(recent_events):
            print(f"\n{i+1}. ID={event.id}, Минута {event.minute}, Тип: {event.event_type}")
            print(f"   Описание: {event.description[:100]}...")
            print(f"   personality_reason: {event.personality_reason or 'ПУСТО'}")
            
            # Проверяем поле напрямую через БД
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT personality_reason FROM matches_matchevent WHERE id = %s", 
                    [event.id]
                )
                db_value = cursor.fetchone()[0]
                print(f"   Значение в БД напрямую: {db_value or 'NULL'}")
    else:
        print("Нет событий для этого матча")
    
    # Шаг 5: Проверяем, как views передает данные
    print("\n\nШАГ 5: Проверка передачи данных в views")
    print("Проверяем код в views.py...")
    
    # Читаем фрагмент views.py
    views_path = os.path.join(os.path.dirname(__file__), 'matches', 'views.py')
    if os.path.exists(views_path):
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'personality_reason' in content:
                print("✓ views.py содержит обработку personality_reason")
            else:
                print("✗ views.py НЕ содержит упоминания personality_reason!")
    
    # Шаг 6: Проверяем шаблон
    print("\nШАГ 6: Проверка шаблона match_detail.html")
    template_path = os.path.join(os.path.dirname(__file__), 'matches', 'templates', 'matches', 'match_detail.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'personality_reason' in content:
                print("✓ match_detail.html содержит отображение personality_reason")
                # Найдем конкретный фрагмент
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'personality_reason' in line:
                        print(f"   Строка {i+1}: {line.strip()}")
            else:
                print("✗ match_detail.html НЕ содержит personality_reason!")
    
    print("\n=== КОНЕЦ ОТЛАДКИ ===")

if __name__ == "__main__":
    test_personality_chain()