#!/usr/bin/env python
"""
Исправление для проблемы с застреванием симуляции матча
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.utils import timezone
from matches.models import Match
from django.conf import settings
from datetime import timedelta

def apply_fix():
    """Применяет исправление к файлу tournaments/tasks.py"""
    
    print("=== ПРИМЕНЕНИЕ ИСПРАВЛЕНИЯ ===\n")
    
    # Читаем текущий файл
    file_path = '/mnt/c/realfootballsim/tournaments/tasks.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Проверяем, нужно ли исправление
    if 'match.started_at is None' in content and 'match.last_minute_update is None' in content:
        print("✓ Файл уже содержит необходимые проверки")
        return False
    
    # Находим функцию simulate_active_matches и добавляем инициализацию времени
    import re
    
    # Паттерн для поиска места после match_locked = Match.objects.select_for_update().get(id=match.id)
    pattern = r'(match_locked = Match\.objects\.select_for_update\(\)\.get\(id=match\.id\))'
    
    replacement = r'''\1

                # Инициализируем время начала и последнего обновления, если не установлены
                if match_locked.started_at is None:
                    match_locked.started_at = timezone.now()
                    match_locked.save(update_fields=['started_at'])
                    logger.info(f"Установлено время начала для матча ID={match_locked.id}")
                
                if match_locked.last_minute_update is None:
                    match_locked.last_minute_update = timezone.now()
                    match_locked.save(update_fields=['last_minute_update'])
                    logger.info(f"Установлено время последнего обновления для матча ID={match_locked.id}")'''
    
    # Применяем замену
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        # Создаем резервную копию
        backup_path = file_path + '.backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✓ Создана резервная копия: {backup_path}")
        
        # Записываем исправленный файл
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"✓ Файл обновлен: {file_path}")
        return True
    else:
        print("✗ Не удалось применить автоматическое исправление")
        print("\nРучное исправление:")
        print_manual_fix()
        return False

def print_manual_fix():
    """Выводит инструкции для ручного исправления"""
    print("""
РУЧНОЕ ИСПРАВЛЕНИЕ:

В файле /mnt/c/realfootballsim/tournaments/tasks.py, в функции simulate_active_matches,
после строки:
    match_locked = Match.objects.select_for_update().get(id=match.id)

Добавьте следующий код:

    # Инициализируем время начала и последнего обновления, если не установлены
    if match_locked.started_at is None:
        match_locked.started_at = timezone.now()
        match_locked.save(update_fields=['started_at'])
        logger.info(f"Установлено время начала для матча ID={match_locked.id}")
    
    if match_locked.last_minute_update is None:
        match_locked.last_minute_update = timezone.now()
        match_locked.save(update_fields=['last_minute_update'])
        logger.info(f"Установлено время последнего обновления для матча ID={match_locked.id}")

Это гарантирует, что поля времени всегда инициализированы для корректной работы
функции advance_match_minutes.
""")

def fix_existing_matches():
    """Исправляет существующие матчи"""
    print("\n=== ИСПРАВЛЕНИЕ СУЩЕСТВУЮЩИХ МАТЧЕЙ ===\n")
    
    # Находим матчи с проблемами
    problematic_matches = Match.objects.filter(
        status='in_progress'
    ).filter(
        models.Q(started_at__isnull=True) | 
        models.Q(last_minute_update__isnull=True)
    )
    
    if problematic_matches.exists():
        print(f"Найдено проблемных матчей: {problematic_matches.count()}")
        
        for match in problematic_matches:
            print(f"\nИсправляем матч ID: {match.id}")
            
            if match.started_at is None:
                match.started_at = timezone.now()
                print("  ✓ Установлено время начала")
            
            if match.last_minute_update is None:
                match.last_minute_update = timezone.now()
                print("  ✓ Установлено время последнего обновления")
            
            # Сбрасываем флаг ожидания для возобновления симуляции
            if match.waiting_for_next_minute and match.current_minute == 1:
                match.waiting_for_next_minute = False
                print("  ✓ Сброшен флаг waiting_for_next_minute")
            
            match.save()
    else:
        print("✓ Проблемных матчей не найдено")

def verify_celery_tasks():
    """Проверяет правильность настройки Celery задач"""
    print("\n=== ПРОВЕРКА CELERY ЗАДАЧ ===\n")
    
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    
    # Проверяем advance-match-minutes
    try:
        task = PeriodicTask.objects.get(name='advance-match-minutes')
        print(f"✓ Задача advance-match-minutes найдена")
        print(f"  - Активна: {task.enabled}")
        print(f"  - Интервал: {task.interval.every} {task.interval.period}")
        
        if not task.enabled:
            task.enabled = True
            task.save()
            print("  ✓ Задача активирована")
            
    except PeriodicTask.DoesNotExist:
        print("✗ Задача advance-match-minutes не найдена!")
        print("  Запустите: python fix_celery_beat_tasks.py")

if __name__ == '__main__':
    try:
        from django.db import models
        
        # Применяем исправления
        code_fixed = apply_fix()
        fix_existing_matches()
        verify_celery_tasks()
        
        print("\n\n=== ИТОГ ===")
        if code_fixed:
            print("✓ Код исправлен. Перезапустите Celery worker для применения изменений.")
        else:
            print("! Требуется ручное исправление кода (см. выше)")
        
        print("\nДля перезапуска Celery:")
        print("1. Остановите текущие процессы (Ctrl+C)")
        print("2. Запустите worker: celery -A realfootballsim worker -l info")
        print("3. Запустите beat: celery -A realfootballsim beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler")
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()