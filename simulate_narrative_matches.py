#!/usr/bin/env python3
"""
Симуляция случайных матчей для генерации нарративных данных
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from clubs.models import Club
from players.models import Player
from matches.models import Match, MatchEvent
from matches.match_simulation import simulate_one_action
from matches.narrative_system import NarrativeAIEngine


def create_random_match():
    """Создает случайный матч между двумя клубами"""
    clubs = list(Club.objects.all())
    if len(clubs) < 2:
        print("Недостаточно клубов для создания матча")
        return None
    
    home_club, away_club = random.sample(clubs, 2)
    
    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        status='in_progress',
        current_minute=1,
        datetime=datetime.now()
    )
    
    print(f"Создан матч: {home_club.name} vs {away_club.name} (ID: {match.id})")
    return match


def simulate_full_match(match):
    """Симулирует полный матч"""
    print(f"\nСимуляция матча: {match.home_team.name} vs {match.away_team.name}")
    
    # Инициализируем нарративы для команд
    home_narratives = NarrativeAIEngine.initialize_club_narratives(match.home_team)
    away_narratives = NarrativeAIEngine.initialize_club_narratives(match.away_team)
    
    print(f"  Домашняя команда - Соперничества: {len(home_narratives['rivalries'])}, Химия: {len(home_narratives['chemistry'])}")
    print(f"  Гостевая команда - Соперничества: {len(away_narratives['rivalries'])}, Химия: {len(away_narratives['chemistry'])}")
    
    actions_count = 0
    max_actions = 150  # Ограничение для симуляции
    
    try:
        while match.current_minute <= 90 and actions_count < max_actions:
            result = simulate_one_action(match)
            actions_count += 1
            
            if result and result.get('event'):
                event = result['event']
                event_type = event.get('event_type', 'unknown')
                
                # Продвигаем минуту матча каждые 3-5 действий
                if actions_count % random.randint(3, 5) == 0:
                    match.current_minute += 1
                
                if event_type in ['goal', 'foul']:
                    print(f"    Мин {match.current_minute}: {event_type.upper()}")
            
            # Сохраняем матч периодически
            if actions_count % 20 == 0:
                match.save()
        
        # Завершаем матч
        match.status = 'finished'
        match.current_minute = 90
        match.save()
        
        print(f"  Финальный счет: {match.home_score}-{match.away_score}")
        print(f"  Всего действий: {actions_count}")
        
        return True
        
    except Exception as e:
        print(f"  Ошибка симуляции: {e}")
        match.status = 'error'
        match.save()
        return False


def get_match_participants(match):
    """Получает игроков, участвовавших в матче"""
    # Получаем игроков из событий матча
    events = MatchEvent.objects.filter(match=match)
    participants = set()
    
    for event in events:
        if event.player:
            participants.add(event.player)
        if event.related_player:
            participants.add(event.related_player)
    
    # Если нет событий, берем случайных игроков из команд
    if not participants:
        home_players = list(match.home_team.player_set.all()[:5])
        away_players = list(match.away_team.player_set.all()[:5])
        participants = set(home_players + away_players)
    
    return list(participants)


def main():
    print("=== СИМУЛЯЦИЯ МАТЧЕЙ ДЛЯ ГЕНЕРАЦИИ НАРРАТИВНЫХ ДАННЫХ ===\n")
    
    simulated_matches = []
    all_participants = []
    
    # Симулируем 5 матчей
    for i in range(5):
        print(f"\n--- МАТЧ {i+1}/5 ---")
        
        match = create_random_match()
        if not match:
            continue
        
        success = simulate_full_match(match)
        if success:
            simulated_matches.append(match)
            participants = get_match_participants(match)
            all_participants.extend(participants)
            print(f"  Участников: {len(participants)}")
        else:
            print(f"  Матч не удалось симулировать")
    
    print(f"\n=== РЕЗУЛЬТАТЫ СИМУЛЯЦИИ ===")
    print(f"Успешно симулировано матчей: {len(simulated_matches)}")
    print(f"Всего участников: {len(set(all_participants))}")
    
    # Показываем статистику нарративных данных
    from matches.models import PlayerRivalry, TeamChemistry, CharacterEvolution, NarrativeEvent
    
    print(f"\nНарративная статистика:")
    print(f"  Соперничества: {PlayerRivalry.objects.count()}")
    print(f"  Командная химия: {TeamChemistry.objects.count()}")
    print(f"  Эволюции характера: {CharacterEvolution.objects.count()}")
    print(f"  Нарративные события: {NarrativeEvent.objects.count()}")
    
    # Выбираем случайного участника для детального анализа
    if all_participants:
        selected_player = random.choice(list(set(all_participants)))
        print(f"\n--- РЕКОМЕНДУЕМЫЙ ИГРОК ДЛЯ АНАЛИЗА ---")
        print(f"ID: {selected_player.id}")
        print(f"Имя: {selected_player.full_name}")
        print(f"Клуб: {selected_player.club.name if selected_player.club else 'Без клуба'}")
        print(f"\nДля детального анализа выполните:")
        print(f"python manage.py view_player_narrative {selected_player.id} --detailed")
    
    print(f"\n=== СИМУЛЯЦИЯ ЗАВЕРШЕНА ===")
    return selected_player.id if all_participants else None


if __name__ == "__main__":
    try:
        selected_id = main()
    except KeyboardInterrupt:
        print("\n\nСимуляция прервана пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()