#!/usr/bin/env python
"""
Проверка проблемы с переходом между минутами в симуляции матча
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.utils import timezone
from matches.models import Match, MatchEvent
from django.conf import settings
from datetime import timedelta

def check_minute_transition_logic():
    """Проверяет логику перехода минут"""
    print("=== ПРОВЕРКА ЛОГИКИ ПЕРЕХОДА МИНУТ ===\n")
    
    print(f"MATCH_MINUTE_REAL_SECONDS = {settings.MATCH_MINUTE_REAL_SECONDS}")
    
    # Находим активный матч
    match = Match.objects.filter(status='in_progress').first()
    if not match:
        print("Нет активных матчей!")
        return
    
    print(f"\nМатч ID: {match.id}")
    print(f"Текущая минута: {match.current_minute}")
    print(f"waiting_for_next_minute: {match.waiting_for_next_minute}")
    print(f"last_minute_update: {match.last_minute_update}")
    
    # Проверяем условия для перехода
    now = timezone.now()
    
    if match.last_minute_update is None:
        print("\nПРОБЛЕМА: last_minute_update не установлен!")
        print("Это значит, что матч начался, но время последнего обновления не было инициализировано")
        return
    
    elapsed = (now - match.last_minute_update).total_seconds()
    print(f"\nПрошло времени с последнего обновления: {elapsed:.1f} секунд")
    print(f"Требуется для перехода: {settings.MATCH_MINUTE_REAL_SECONDS} секунд")
    
    # Проверяем условия функции advance_match_minutes
    print("\nПроверка условий для перехода на следующую минуту:")
    
    condition1 = match.waiting_for_next_minute
    print(f"1. waiting_for_next_minute = {condition1} {'✓' if condition1 else '✗'}")
    
    condition2 = elapsed >= settings.MATCH_MINUTE_REAL_SECONDS
    print(f"2. Прошло достаточно времени = {condition2} {'✓' if condition2 else '✗'}")
    
    condition3 = match.current_minute < 90
    print(f"3. Минута < 90 = {condition3} {'✓' if condition3 else '✗'}")
    
    if condition1 and condition2 and condition3:
        print("\n✓ ВСЕ УСЛОВИЯ ВЫПОЛНЕНЫ - минута должна переключиться!")
    else:
        print("\n✗ Не все условия выполнены для перехода")
        
        if not condition1:
            print("\nПРОБЛЕМА: waiting_for_next_minute = False")
            print("Это означает, что симуляция действий не установила флаг ожидания")
            print("Возможные причины:")
            print("- Действие не завершилось (continue=True)")
            print("- Ошибка в simulate_one_action")

def test_advance_minute_directly():
    """Напрямую тестирует функцию advance_match_minutes"""
    print("\n\n=== ПРЯМОЙ ТЕСТ ФУНКЦИИ advance_match_minutes ===\n")
    
    from tournaments.tasks import advance_match_minutes
    
    # Подготавливаем матч для теста
    match = Match.objects.filter(status='in_progress').first()
    if not match:
        print("Нет активных матчей!")
        return
    
    print(f"Подготовка матча ID {match.id} для теста...")
    
    # Устанавливаем условия для успешного перехода
    match.waiting_for_next_minute = True
    match.last_minute_update = timezone.now() - timedelta(seconds=settings.MATCH_MINUTE_REAL_SECONDS + 1)
    old_minute = match.current_minute
    match.save()
    
    print(f"Установлены параметры:")
    print(f"- waiting_for_next_minute = True")
    print(f"- last_minute_update установлен в прошлое")
    print(f"- Текущая минута: {old_minute}")
    
    # Вызываем функцию
    print("\nВызываем advance_match_minutes()...")
    result = advance_match_minutes()
    print(f"Результат: {result}")
    
    # Проверяем изменения
    match.refresh_from_db()
    print(f"\nПосле вызова:")
    print(f"- Минута изменилась: {old_minute} -> {match.current_minute} {'✓' if match.current_minute > old_minute else '✗'}")
    print(f"- waiting_for_next_minute = {match.waiting_for_next_minute} {'✓' if not match.waiting_for_next_minute else '✗'}")
    
    # Проверяем создание события
    info_event = MatchEvent.objects.filter(
        match=match,
        minute=match.current_minute,
        event_type='info'
    ).first()
    
    if info_event:
        print(f"✓ Создано информационное событие: {info_event.description}")
    else:
        print("✗ Информационное событие не создано")

def check_simulation_flow():
    """Проверяет поток симуляции"""
    print("\n\n=== ПРОВЕРКА ПОТОКА СИМУЛЯЦИИ ===\n")
    
    from matches.match_simulation import simulate_one_action
    
    match = Match.objects.filter(status='in_progress').first()
    if not match:
        print("Нет активных матчей!")
        return
    
    print(f"Симулируем действие для матча ID {match.id}")
    print(f"Начальное состояние: минута {match.current_minute}, waiting_for_next_minute={match.waiting_for_next_minute}")
    
    # Симулируем действие
    result = simulate_one_action(match)
    
    print(f"\nРезультат симуляции:")
    print(f"- action_type: {result.get('action_type')}")
    print(f"- continue: {result.get('continue', True)}")
    print(f"- event: {'Да' if result.get('event') else 'Нет'}")
    
    # Проверяем, должен ли был установиться флаг
    if result.get('continue', True) is False:
        print("\n✓ Действие завершилось, должен установиться waiting_for_next_minute")
    else:
        print("\n✗ Действие продолжается, флаг не должен устанавливаться")

if __name__ == '__main__':
    try:
        check_minute_transition_logic()
        test_advance_minute_directly()
        check_simulation_flow()
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()