#!/usr/bin/env python
import os
import sys
import django
import time
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match
from django.utils import timezone

def monitor_matches(duration=60):
    """Мониторит активные матчи в течение указанного времени (в секундах)"""
    
    print(f"=== Мониторинг матчей в течение {duration} секунд ===\n")
    print("Нажмите Ctrl+C для остановки\n")
    
    start_time = time.time()
    previous_states = {}
    
    try:
        while time.time() - start_time < duration:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Проверка состояния матчей:")
            print("-" * 60)
            
            active_matches = Match.objects.filter(status='in_progress')
            
            if not active_matches.exists():
                print("Нет активных матчей")
            else:
                for match in active_matches:
                    match_key = match.id
                    current_state = {
                        'minute': match.current_minute,
                        'score': f"{match.home_score}-{match.away_score}",
                        'zone': match.current_zone,
                        'waiting': match.waiting_for_next_minute,
                        'started_at': match.started_at,
                        'last_update': match.last_minute_update
                    }
                    
                    # Проверяем изменения
                    if match_key in previous_states:
                        prev = previous_states[match_key]
                        changes = []
                        
                        if prev['minute'] != current_state['minute']:
                            changes.append(f"минута: {prev['minute']} -> {current_state['minute']}")
                        if prev['score'] != current_state['score']:
                            changes.append(f"счёт: {prev['score']} -> {current_state['score']}")
                        if prev['zone'] != current_state['zone']:
                            changes.append(f"зона: {prev['zone']} -> {current_state['zone']}")
                        if prev['waiting'] != current_state['waiting']:
                            changes.append(f"ожидание: {prev['waiting']} -> {current_state['waiting']}")
                        
                        if changes:
                            change_str = " | ".join(changes)
                            print(f"ID {match.id}: {match.home_team.name} vs {match.away_team.name}")
                            print(f"  [ИЗМЕНЕНИЯ] {change_str}")
                        else:
                            print(f"ID {match.id}: мин. {current_state['minute']}, счёт {current_state['score']}, зона {current_state['zone']}")
                    else:
                        print(f"ID {match.id}: {match.home_team.name} vs {match.away_team.name}")
                        print(f"  [НОВЫЙ] мин. {current_state['minute']}, счёт {current_state['score']}, зона {current_state['zone']}")
                    
                    # Проверяем временные поля
                    if current_state['started_at'] is None:
                        print(f"  [ОШИБКА] started_at не установлен!")
                    if current_state['last_update'] is None:
                        print(f"  [ОШИБКА] last_minute_update не установлен!")
                    
                    previous_states[match_key] = current_state
            
            time.sleep(5)  # Проверяем каждые 5 секунд
            
    except KeyboardInterrupt:
        print("\n\nМониторинг остановлен пользователем")
    
    print(f"\n=== Мониторинг завершён ===")
    print(f"Общее время: {int(time.time() - start_time)} секунд")

if __name__ == "__main__":
    # Можно передать время мониторинга как аргумент
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    monitor_matches(duration)