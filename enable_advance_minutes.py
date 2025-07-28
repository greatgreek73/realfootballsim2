#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django_celery_beat.models import PeriodicTask

print("=== Включение задачи advance-match-minutes ===\n")

try:
    task = PeriodicTask.objects.get(name='advance-match-minutes')
    
    print(f"Задача найдена: {task.name}")
    print(f"Текущий статус: {'Включена' if task.enabled else 'ОТКЛЮЧЕНА'}")
    
    if not task.enabled:
        task.enabled = True
        task.save()
        print("\n[SUCCESS] Задача включена!")
        print("Celery Beat должен начать выполнять задачу в течение 5 секунд")
    else:
        print("\nЗадача уже включена")
        
except PeriodicTask.DoesNotExist:
    print("[ERROR] Задача advance-match-minutes не найдена в БД!")
    
print("\nПерезапустите Celery Beat для немедленного применения изменений")