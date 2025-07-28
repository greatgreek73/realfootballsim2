#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match
from django.utils import timezone
from django.db import transaction

def fix_stuck_matches():
    """Исправляет застрявшие матчи, устанавливая необходимые временные поля"""
    
    print("=== Поиск застрявших матчей ===\n")
    
    # Ищем активные матчи
    active_matches = Match.objects.filter(status='in_progress')
    
    if not active_matches.exists():
        print("Активных матчей не найдено.")
        return
    
    print(f"Найдено {active_matches.count()} активных матчей\n")
    
    fixed_count = 0
    
    for match in active_matches:
        print(f"Матч ID: {match.id}")
        print(f"  {match.home_team.name} vs {match.away_team.name}")
        print(f"  Текущая минута: {match.current_minute}")
        print(f"  Счёт: {match.home_score} - {match.away_score}")
        
        changes_made = False
        
        with transaction.atomic():
            # Блокируем матч для обновления
            match_locked = Match.objects.select_for_update().get(id=match.id)
            
            # Проверяем и исправляем started_at
            if match_locked.started_at is None:
                match_locked.started_at = timezone.now()
                print(f"  [OK] Установлено время начала: {match_locked.started_at}")
                changes_made = True
            else:
                print(f"  [INFO] Время начала уже установлено: {match_locked.started_at}")
            
            # Проверяем и исправляем last_minute_update
            if match_locked.last_minute_update is None:
                match_locked.last_minute_update = timezone.now()
                print(f"  [OK] Установлено время последнего обновления: {match_locked.last_minute_update}")
                changes_made = True
            else:
                print(f"  [INFO] Время последнего обновления уже установлено: {match_locked.last_minute_update}")
            
            # Проверяем флаг ожидания
            if match_locked.waiting_for_next_minute:
                print(f"  [WAIT] Матч ожидает следующую минуту")
            
            if changes_made:
                match_locked.save()
                fixed_count += 1
                print(f"  [SAVED] Изменения сохранены")
            
        print()
    
    print(f"\n=== Итоги ===")
    print(f"Исправлено матчей: {fixed_count}")
    print(f"Всего активных матчей: {active_matches.count()}")
    
    if fixed_count > 0:
        print("\n[SUCCESS] Матчи должны продолжить симуляцию автоматически.")
        print("Убедитесь, что запущены Celery Worker и Celery Beat!")

if __name__ == "__main__":
    fix_stuck_matches()