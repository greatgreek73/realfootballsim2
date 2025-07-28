#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from players.models import Player

# Найти последний матч
match = Match.objects.order_by('-datetime').first()

if match:
    print(f"Добавляем тестовое событие в матч {match.id}: {match.home_team.name} vs {match.away_team.name}")
    
    # Найти игрока
    player = Player.objects.filter(club=match.home_team).first()
    
    if player:
        # Создать событие с personality_reason
        event = MatchEvent.objects.create(
            match=match,
            minute=45,
            event_type='goal',
            player=player,
            description=f"ТЕСТОВЫЙ ГОЛ! {player.first_name} {player.last_name} забивает великолепный гол!",
            personality_reason="Повлияла черта: Clutch Player - проявляет себя в важные моменты матча"
        )
        
        print(f"Создано событие ID={event.id}:")
        print(f"  Минута: {event.minute}")
        print(f"  Тип: {event.event_type}")
        print(f"  Описание: {event.description}")
        print(f"  Personality: {event.personality_reason}")
        print(f"\nПроверьте страницу матча: /matches/{match.id}/")
    else:
        print("Не найден игрок для тестирования")
else:
    print("Не найден матч для тестирования")