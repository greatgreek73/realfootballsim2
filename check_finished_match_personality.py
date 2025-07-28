#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from django.db.models import Count

# Найдем последний завершенный матч с событиями
matches = Match.objects.filter(
    status='finished'
).annotate(
    event_count=Count('events')
).filter(
    event_count__gt=0
).order_by('-datetime')[:5]

print("=== CHECKING FINISHED MATCHES FOR personality_reason ===\n")

for match in matches:
    print(f"\nMatch: {match.home_team.name} vs {match.away_team.name}")
    print(f"Date: {match.datetime}")
    print(f"Status: {match.status}")
    print(f"Events count: {match.event_count}")
    
    # Проверяем события с personality_reason
    events_with_reason = MatchEvent.objects.filter(
        match=match,
        personality_reason__isnull=False
    ).exclude(personality_reason='')
    
    print(f"Events with personality_reason: {events_with_reason.count()}")
    
    if events_with_reason.exists():
        print("\nFirst 5 events with personality_reason:")
        for event in events_with_reason[:5]:
            print(f"  - [{event.minute}'] {event.event_type}: {event.personality_reason}")
    
    # Проверяем общее количество событий для сравнения
    total_events = MatchEvent.objects.filter(match=match).count()
    print(f"Total events in match: {total_events}")
    
    if events_with_reason.count() > 0:
        percentage = (events_with_reason.count() / total_events) * 100
        print(f"Percentage with personality_reason: {percentage:.1f}%")