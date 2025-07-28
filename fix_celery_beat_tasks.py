#!/usr/bin/env python
"""
Скрипт для исправления конфигурации Celery Beat задач
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.conf import settings
import json

def check_and_fix_celery_beat_tasks():
    """Проверяет и исправляет периодические задачи Celery Beat"""
    print("=== ПРОВЕРКА И ИСПРАВЛЕНИЕ CELERY BEAT ЗАДАЧ ===\n")
    
    # Проверяем существующие задачи
    existing_tasks = PeriodicTask.objects.all()
    print(f"Существующие задачи ({existing_tasks.count()}):")
    for task in existing_tasks:
        print(f"- {task.name}: {task.task} (Активна: {task.enabled})")
    
    # Проверяем конкретные задачи
    required_tasks = {
        'simulate-active-matches': {
            'task': 'tournaments.simulate_active_matches',
            'interval_seconds': 2,  # Каждые 2 секунды для пошаговой симуляции
        },
        'advance-match-minutes': {
            'task': 'tournaments.advance_match_minutes', 
            'interval_seconds': 1,  # Каждую секунду проверяем переход минут
        }
    }
    
    print("\n\nПроверка и создание/обновление необходимых задач:")
    
    for task_name, task_config in required_tasks.items():
        print(f"\n{task_name}:")
        
        # Получаем или создаем интервал
        interval, created = IntervalSchedule.objects.get_or_create(
            every=task_config['interval_seconds'],
            period=IntervalSchedule.SECONDS
        )
        if created:
            print(f"  ✓ Создан интервал: каждые {task_config['interval_seconds']} сек")
        else:
            print(f"  - Используется существующий интервал: каждые {task_config['interval_seconds']} сек")
        
        # Получаем или создаем задачу
        task, created = PeriodicTask.objects.get_or_create(
            name=task_name,
            defaults={
                'task': task_config['task'],
                'interval': interval,
                'enabled': True,
                'kwargs': json.dumps({})
            }
        )
        
        if created:
            print(f"  ✓ Создана новая задача: {task_config['task']}")
        else:
            # Обновляем существующую задачу
            updated = False
            if task.task != task_config['task']:
                task.task = task_config['task']
                updated = True
            if task.interval != interval:
                task.interval = interval
                updated = True
            if not task.enabled:
                task.enabled = True
                updated = True
            
            if updated:
                task.save()
                print(f"  ✓ Обновлена существующая задача")
            else:
                print(f"  - Задача уже настроена правильно")
    
    # Отключаем лишние задачи
    print("\n\nПроверка лишних задач:")
    all_task_names = set(required_tasks.keys())
    for task in existing_tasks:
        if task.name not in all_task_names and task.enabled:
            print(f"- Отключаем лишнюю задачу: {task.name}")
            task.enabled = False
            task.save()

def test_task_execution():
    """Тестирует выполнение задач напрямую"""
    print("\n\n=== ТЕСТ ВЫПОЛНЕНИЯ ЗАДАЧ ===\n")
    
    from tournaments.tasks import simulate_active_matches, advance_match_minutes
    from matches.models import Match
    
    # Проверяем наличие активных матчей
    active_matches = Match.objects.filter(status='in_progress')
    print(f"Активных матчей: {active_matches.count()}")
    
    if active_matches.exists():
        match = active_matches.first()
        print(f"\nТестируем с матчем ID: {match.id}")
        print(f"Минута: {match.current_minute}, waiting_for_next_minute: {match.waiting_for_next_minute}")
        
        # Тест simulate_active_matches
        print("\n1. Тестируем simulate_active_matches:")
        try:
            result = simulate_active_matches.apply()
            print(f"   Результат: {result.result}")
            match.refresh_from_db()
            print(f"   После: waiting_for_next_minute = {match.waiting_for_next_minute}")
        except Exception as e:
            print(f"   Ошибка: {e}")
        
        # Тест advance_match_minutes
        print("\n2. Тестируем advance_match_minutes:")
        try:
            result = advance_match_minutes.apply()
            print(f"   Результат: {result.result}")
            match.refresh_from_db() 
            print(f"   После: минута = {match.current_minute}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    else:
        print("Нет активных матчей для тестирования")

def check_celery_worker():
    """Проверяет статус Celery worker"""
    print("\n\n=== ПРОВЕРКА CELERY WORKER ===\n")
    
    from celery import current_app
    
    # Проверяем зарегистрированные задачи
    print("Зарегистрированные задачи в Celery:")
    for task_name in sorted(current_app.tasks.keys()):
        if 'tournaments' in task_name or 'matches' in task_name:
            print(f"- {task_name}")
    
    # Проверяем активные воркеры
    print("\nПопытка проверить активные воркеры:")
    try:
        stats = current_app.control.inspect().stats()
        if stats:
            print(f"Найдено воркеров: {len(stats)}")
            for worker_name, worker_stats in stats.items():
                print(f"- {worker_name}")
        else:
            print("✗ Воркеры не найдены или не отвечают!")
            print("  Убедитесь, что Celery worker запущен")
    except Exception as e:
        print(f"✗ Ошибка при проверке воркеров: {e}")

if __name__ == '__main__':
    try:
        check_and_fix_celery_beat_tasks()
        test_task_execution()
        check_celery_worker()
        
        print("\n\n=== РЕКОМЕНДАЦИИ ===")
        print("1. Убедитесь, что Celery worker запущен:")
        print("   celery -A realfootballsim worker -l info")
        print("\n2. Убедитесь, что Celery beat запущен:")
        print("   celery -A realfootballsim beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler")
        print("\n3. Для мониторинга используйте:")
        print("   celery -A realfootballsim flower")
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()