#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent

# Найти последние события с personality_reason
print("=== Проверка personality_reason в событиях матчей ===\n")

# Получаем последние 5 матчей
recent_matches = Match.objects.order_by('-datetime')[:5]

for match in recent_matches:
    print(f"\nМатч {match.id}: {match.home_team.name} vs {match.away_team.name} (статус: {match.status})")
    
    # Получаем события с personality_reason
    events_with_reason = match.events.exclude(personality_reason__isnull=True).exclude(personality_reason='')
    
    if events_with_reason.exists():
        print(f"  Найдено {events_with_reason.count()} событий с personality_reason:")
        for event in events_with_reason[:3]:  # Показываем первые 3
            print(f"    - Минута {event.minute}: {event.event_type}")
            print(f"      Описание: {event.description}")
            print(f"      Personality: {event.personality_reason}")
    else:
        print("  Нет событий с personality_reason")
        
    # Проверяем общее количество событий
    total_events = match.events.count()
    print(f"  Всего событий в матче: {total_events}")

# Общая статистика
print("\n=== Общая статистика ===")
total_events_with_reason = MatchEvent.objects.exclude(personality_reason__isnull=True).exclude(personality_reason='').count()
total_events = MatchEvent.objects.count()
print(f"Всего событий с personality_reason: {total_events_with_reason} из {total_events}")

# Примеры personality_reason
print("\n=== Примеры уникальных personality_reason ===")
unique_reasons = MatchEvent.objects.exclude(personality_reason__isnull=True).exclude(personality_reason='').values_list('personality_reason', flat=True).distinct()[:10]
for reason in unique_reasons:
    print(f"  - {reason}")