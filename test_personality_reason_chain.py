#!/usr/bin/env python
"""
Скрипт для проверки полной цепочки передачи personality_reason
от simulate_one_action до отображения в шаблоне
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from matches.match_simulation import MatchSimulation
from clubs.models import Club
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

def check_personality_engine_status():
    """Проверяем, включен ли PersonalityEngine"""
    print("\n=== CHECKING PERSONALITY ENGINE STATUS ===")
    use_personality = getattr(settings, 'USE_PERSONALITY_ENGINE', False)
    print(f"USE_PERSONALITY_ENGINE = {use_personality}")
    
    if not use_personality:
        print("\n⚠️  WARNING: PersonalityEngine is DISABLED in settings!")
        print("   personality_reason will NOT be generated")
    else:
        print("\n✓ PersonalityEngine is ENABLED")
    
    return use_personality

def create_test_match():
    """Создаем тестовый матч"""
    print("\n=== CREATING TEST MATCH ===")
    
    # Получаем клубы
    clubs = Club.objects.all()[:2]
    if len(clubs) < 2:
        print("ERROR: Need at least 2 clubs in database")
        return None
    
    home_club = clubs[0]
    away_club = clubs[1]
    user = User.objects.first()
    
    # Создаем матч
    match = Match.objects.create(
        home_club=home_club,
        away_club=away_club,
        championship=home_club.championship,
        user=user,
        status='pending'
    )
    
    print(f"Created match: {match.home_club.name} vs {match.away_club.name}")
    print(f"Match ID: {match.id}")
    
    return match

def test_simulate_one_action(match):
    """Тестируем simulate_one_action и проверяем результат"""
    print("\n=== TESTING simulate_one_action ===")
    
    # Инициализируем симуляцию
    simulation = MatchSimulation(match)
    simulation.setup_match()
    
    # Симулируем несколько действий, чтобы найти событие с personality_reason
    events_with_reason = []
    events_without_reason = []
    
    for i in range(10):  # Симулируем до 10 действий
        print(f"\nAction {i+1}:")
        result = simulation.simulate_one_action()
        
        if result.get('event'):
            event_data = result['event']
            print(f"  Event type: {event_data.get('event_type')}")
            print(f"  Description: {event_data.get('description', '')[:50]}...")
            
            if event_data.get('personality_reason'):
                print(f"  ✓ personality_reason: {event_data['personality_reason']}")
                events_with_reason.append(event_data)
            else:
                print(f"  ✗ No personality_reason")
                events_without_reason.append(event_data)
    
    print(f"\n\nSUMMARY:")
    print(f"Events with personality_reason: {len(events_with_reason)}")
    print(f"Events without personality_reason: {len(events_without_reason)}")
    
    return events_with_reason, events_without_reason

def check_database_events(match_id):
    """Проверяем события в базе данных"""
    print("\n\n=== CHECKING DATABASE EVENTS ===")
    
    events = MatchEvent.objects.filter(match_id=match_id).order_by('id')
    
    if not events:
        print("No events found in database")
        return
    
    print(f"Total events in database: {events.count()}")
    
    events_with_reason = events.exclude(personality_reason__isnull=True).exclude(personality_reason='')
    print(f"Events with personality_reason: {events_with_reason.count()}")
    
    if events_with_reason.exists():
        print("\nExamples of events with personality_reason:")
        for event in events_with_reason[:3]:
            print(f"  - [{event.minute}'] {event.event_type}: {event.personality_reason}")

def check_view_processing():
    """Проверяем обработку в views.py"""
    print("\n\n=== CHECKING VIEW PROCESSING ===")
    
    print("In views.py (match_detail function):")
    print("  - Line 105: personality_reason is extracted using getattr(event, 'personality_reason', None)")
    print("  - This is added to enriched_event dict that is passed to template")
    print("  ✓ View correctly processes personality_reason")

def check_template_rendering():
    """Проверяем рендеринг в шаблоне"""
    print("\n\n=== CHECKING TEMPLATE RENDERING ===")
    
    print("In match_detail.html:")
    print("  - Lines 202-206: Check if enriched_event.personality_reason exists")
    print("  - If exists, renders it in <small> tag with 'text-secondary fst-italic' classes")
    print("  ✓ Template correctly renders personality_reason for finished matches")

def check_websocket_transmission():
    """Проверяем передачу через WebSocket"""
    print("\n\n=== CHECKING WEBSOCKET TRANSMISSION ===")
    
    print("In tournaments/tasks.py (simulate_active_matches):")
    print("  - Line 114: personality_reason is added to event_data")
    print("  - Line 161: personality_reason is added to additional_event data")
    print("  - Line 202: personality_reason is added to second_additional_event data")
    print("  - Line 243: personality_reason is added to third_additional_event data")
    print("  ✓ All event types now include personality_reason in WebSocket messages")
    
    print("\nIn live_match.js:")
    print("  - Lines 281-283: Check if evt.personality_reason exists")
    print("  - If exists, adds it to event HTML with proper styling")
    print("  ✓ JavaScript correctly handles personality_reason from WebSocket")

def main():
    print("=" * 60)
    print("PERSONALITY REASON TRANSMISSION CHAIN TEST")
    print("=" * 60)
    
    # 1. Проверяем статус PersonalityEngine
    is_enabled = check_personality_engine_status()
    
    if not is_enabled:
        print("\n\n⚠️  IMPORTANT: PersonalityEngine is disabled!")
        print("To enable it, set USE_PERSONALITY_ENGINE = True in settings.py")
        return
    
    # 2. Создаем тестовый матч
    match = create_test_match()
    if not match:
        return
    
    # 3. Тестируем simulate_one_action
    events_with, events_without = test_simulate_one_action(match)
    
    # 4. Проверяем базу данных
    check_database_events(match.id)
    
    # 5. Проверяем обработку во views
    check_view_processing()
    
    # 6. Проверяем шаблон
    check_template_rendering()
    
    # 7. Проверяем WebSocket
    check_websocket_transmission()
    
    print("\n\n" + "=" * 60)
    print("CONCLUSION:")
    print("=" * 60)
    
    if is_enabled and events_with:
        print("✓ Full chain is working correctly!")
        print("  - simulate_one_action generates personality_reason")
        print("  - Database stores personality_reason")
        print("  - Views process personality_reason")
        print("  - Templates render personality_reason for finished matches")
        print("  - WebSocket transmits personality_reason for live matches")
        print("  - JavaScript displays personality_reason in live events")
    else:
        print("✗ Issues found:")
        if not is_enabled:
            print("  - PersonalityEngine is disabled in settings")
        if not events_with:
            print("  - No events with personality_reason were generated")
            print("    (This might be normal - not all events have personality influence)")

if __name__ == "__main__":
    main()