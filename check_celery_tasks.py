#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django_celery_beat.models import PeriodicTask, IntervalSchedule

print("=== Проверка периодических задач Celery ===\n")

# Проверяем все активные задачи
tasks = PeriodicTask.objects.filter(enabled=True)
print(f"Всего активных задач: {tasks.count()}\n")

for task in tasks:
    print(f"Задача: {task.name}")
    print(f"  - Task: {task.task}")
    print(f"  - Enabled: {task.enabled}")
    if task.interval:
        print(f"  - Interval: {task.interval.every} {task.interval.period}")
    print()

# Специально проверяем advance-match-minutes
print("\n=== Проверка advance-match-minutes ===")
try:
    advance_task = PeriodicTask.objects.get(name='advance-match-minutes')
    print(f"Задача найдена!")
    print(f"  - Enabled: {advance_task.enabled}")
    print(f"  - Task: {advance_task.task}")
    if advance_task.interval:
        print(f"  - Interval: {advance_task.interval.every} {advance_task.interval.period}")
except PeriodicTask.DoesNotExist:
    print("Задача НЕ НАЙДЕНА в базе данных!")
    print("\nСоздаём задачу...")
    
    # Создаем интервал 1 секунда
    interval, created = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.SECONDS,
    )
    
    # Создаем задачу
    task = PeriodicTask.objects.create(
        name='advance-match-minutes',
        task='tournaments.advance_match_minutes',
        interval=interval,
        enabled=True
    )
    print(f"Задача создана: {task.name}")