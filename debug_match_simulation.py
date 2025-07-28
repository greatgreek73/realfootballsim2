#!/usr/bin/env python
"""
Диагностический скрипт для проверки проблемы с застреванием симуляции матча
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.utils import timezone
from matches.models import Match, MatchEvent
from tournaments.tasks import simulate_active_matches, advance_match_minutes
from django.core.cache import cache
import time

def analyze_stuck_matches():
    print("=== АНАЛИЗ ЗАСТРЯВШИХ МАТЧЕЙ ===\n")
    
    # Проверяем все матчи со статусом in_progress
    in_progress_matches = Match.objects.filter(status='in_progress')
    print(f"Найдено матчей в процессе: {in_progress_matches.count()}")
    
    for match in in_progress_matches:
        print(f"\nМатч ID: {match.id}")
        print(f"  Текущая минута: {match.current_minute}")
        print(f"  Счет: {match.home_score} - {match.away_score}")
        print(f"  Ожидание следующей минуты: {match.waiting_for_next_minute}")
        print(f"  Последнее обновление минуты: {match.last_minute_update}")
        print(f"  Начало матча: {match.started_at}")
        
        # Проверяем кеш действий
        cache_key = f"match_{match.id}_actions_in_minute"
        actions_count = cache.get(cache_key, 0)
        print(f"  Количество действий в текущей минуте (из кеша): {actions_count}")
        
        # Проверяем последние события
        last_events = MatchEvent.objects.filter(match=match).order_by('-minute', '-id')[:5]
        print(f"  Последние события:")
        for event in last_events:
            print(f"    Минута {event.minute}: {event.event_type} - {event.description[:50]}...")
        
        # Проверяем временную разницу
        if match.last_minute_update:
            elapsed = (timezone.now() - match.last_minute_update).total_seconds()
            print(f"  Прошло секунд с последнего обновления: {elapsed:.1f}")
            print(f"  Требуется секунд для перехода: {20}")  # MATCH_MINUTE_REAL_SECONDS

def test_minute_advance():
    """Тестируем переход на следующую минуту"""
    print("\n\n=== ТЕСТ ПЕРЕХОДА НА СЛЕДУЮЩУЮ МИНУТУ ===\n")
    
    in_progress_matches = Match.objects.filter(status='in_progress')
    if not in_progress_matches.exists():
        print("Нет активных матчей для тестирования")
        return
    
    match = in_progress_matches.first()
    print(f"Тестируем матч ID: {match.id}")
    print(f"Текущая минута: {match.current_minute}")
    print(f"waiting_for_next_minute: {match.waiting_for_next_minute}")
    
    # Принудительно устанавливаем флаг ожидания
    print("\nУстанавливаем waiting_for_next_minute = True...")
    match.waiting_for_next_minute = True
    match.save()
    
    # Вызываем функцию перехода минут
    print("\nВызываем advance_match_minutes()...")
    result = advance_match_minutes()
    print(f"Результат: {result}")
    
    # Проверяем результат
    match.refresh_from_db()
    print(f"\nПосле вызова:")
    print(f"  Текущая минута: {match.current_minute}")
    print(f"  waiting_for_next_minute: {match.waiting_for_next_minute}")

def simulate_one_action_test():
    """Тестируем симуляцию одного действия"""
    print("\n\n=== ТЕСТ СИМУЛЯЦИИ ОДНОГО ДЕЙСТВИЯ ===\n")
    
    print("Вызываем simulate_active_matches()...")
    result = simulate_active_matches.apply()
    print(f"Результат: {result.result}")
    
    # Проверяем состояние после симуляции
    in_progress_matches = Match.objects.filter(status='in_progress')
    for match in in_progress_matches:
        print(f"\nМатч ID: {match.id} после симуляции:")
        print(f"  waiting_for_next_minute: {match.waiting_for_next_minute}")
        print(f"  current_minute: {match.current_minute}")

def check_celery_beat():
    """Проверяем настройки Celery Beat"""
    print("\n\n=== ПРОВЕРКА CELERY BEAT ===\n")
    
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    
    # Проверяем периодические задачи
    tasks = PeriodicTask.objects.all()
    print(f"Всего периодических задач: {tasks.count()}")
    
    for task in tasks:
        print(f"\nЗадача: {task.name}")
        print(f"  Активна: {task.enabled}")
        print(f"  Task: {task.task}")
        if hasattr(task, 'interval') and task.interval:
            print(f"  Интервал: каждые {task.interval.every} {task.interval.period}")
        print(f"  Последний запуск: {task.last_run_at}")

def fix_stuck_match():
    """Попытка исправить застрявший матч"""
    print("\n\n=== ПОПЫТКА ИСПРАВИТЬ ЗАСТРЯВШИЙ МАТЧ ===\n")
    
    in_progress_matches = Match.objects.filter(status='in_progress')
    if not in_progress_matches.exists():
        print("Нет активных матчей для исправления")
        return
    
    match = in_progress_matches.first()
    print(f"Исправляем матч ID: {match.id}")
    
    # Сброс флагов
    match.waiting_for_next_minute = False
    match.last_minute_update = timezone.now()
    match.save()
    
    # Очистка кеша
    cache_key = f"match_{match.id}_actions_in_minute"
    cache.delete(cache_key)
    
    print("Флаги сброшены, кеш очищен")
    
    # Пробуем симулировать несколько действий
    print("\nЗапускаем симуляцию...")
    for i in range(3):
        print(f"\nИтерация {i+1}:")
        result = simulate_active_matches.apply()
        print(f"Результат: {result.result}")
        time.sleep(1)
        
        match.refresh_from_db()
        print(f"Минута: {match.current_minute}, waiting_for_next_minute: {match.waiting_for_next_minute}")

if __name__ == '__main__':
    try:
        analyze_stuck_matches()
        test_minute_advance()
        simulate_one_action_test()
        check_celery_beat()
        
        # Спрашиваем, нужно ли исправить
        response = input("\n\nПопытаться исправить застрявший матч? (y/n): ")
        if response.lower() == 'y':
            fix_stuck_match()
            
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()