#!/usr/bin/env python3
"""
Тестирование Phase 3: Narrative System

Тестирует интеграцию нарративной системы в симуляцию матчей
"""

import os
import sys
import django
import random
from datetime import date, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.conf import settings
from clubs.models import Club
from players.models import Player
from matches.models import Match, MatchEvent, PlayerRivalry, TeamChemistry, CharacterEvolution, NarrativeEvent
from matches.narrative_system import NarrativeAIEngine, RivalryManager, ChemistryCalculator, EvolutionEngine
from matches.match_simulation import simulate_one_action


def test_narrative_system():
    """Основная тестовая функция"""
    
    print("=== ТЕСТИРОВАНИЕ PHASE 3: NARRATIVE SYSTEM ===\n")
    
    # Включаем PersonalityEngine для тестирования
    print(f"PersonalityEngine включен: {getattr(settings, 'USE_PERSONALITY_ENGINE', False)}")
    
    # 1. Тестируем создание соперничества
    print("\n1. ТЕСТИРОВАНИЕ RIVALRIES")
    test_rivalries()
    
    # 2. Тестируем химию команды
    print("\n2. ТЕСТИРОВАНИЕ TEAM CHEMISTRY")
    test_team_chemistry()
    
    # 3. Тестируем эволюцию характера
    print("\n3. ТЕСТИРОВАНИЕ CHARACTER EVOLUTION")
    test_character_evolution()
    
    # 4. Тестируем генерацию нарративных событий
    print("\n4. ТЕСТИРОВАНИЕ NARRATIVE EVENTS")
    test_narrative_events()
    
    # 5. Интеграционное тестирование
    print("\n5. ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ")
    test_integration()
    
    print("\n=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")


def test_rivalries():
    """Тестирует систему соперничества"""
    
    # Получаем двух игроков
    players = list(Player.objects.all()[:2])
    if len(players) < 2:
        print("[FAIL] Недостаточно игроков для тестирования")
        return
    
    player1, player2 = players[0], players[1]
    print(f"Тестируем соперничество: {player1.full_name} vs {player2.full_name}")
    
    # Создаем соперничество
    rivalry = RivalryManager.create_rivalry(
        player1, player2, 
        rivalry_type='competitive', 
        intensity='moderate'
    )
    
    if rivalry:
        print(f"[OK] Соперничество создано: {rivalry}")
        print(f"   Тип: {rivalry.rivalry_type}")
        print(f"   Интенсивность: {rivalry.intensity}")
        print(f"   Модификатор агрессии: {rivalry.aggression_modifier}")
        print(f"   Модификатор производительности: {rivalry.performance_modifier}")
        
        # Тестируем обновление взаимодействия
        updated_rivalry = RivalryManager.update_rivalry_interaction(
            player1, player2, 'aggressive'
        )
        if updated_rivalry:
            print(f"[OK] Взаимодействие обновлено, счетчик: {updated_rivalry.interaction_count}")
    else:
        print("[FAIL] Не удалось создать соперничество")


def test_team_chemistry():
    """Тестирует систему командной химии"""
    
    # Получаем игроков из одного клуба
    club = Club.objects.first()
    if not club:
        print("[FAIL] Не найдено клубов")
        return
        
    players = list(club.player_set.all()[:2])
    if len(players) < 2:
        print("[FAIL] Недостаточно игроков в клубе")
        return
    
    player1, player2 = players[0], players[1]
    print(f"Тестируем химию: {player1.full_name} + {player2.full_name}")
    
    # Создаем химию
    chemistry = ChemistryCalculator.create_chemistry(
        player1, player2,
        chemistry_type='friendship',
        strength=0.7
    )
    
    if chemistry:
        print(f"[OK] Химия создана: {chemistry}")
        print(f"   Тип: {chemistry.chemistry_type}")
        print(f"   Сила: {chemistry.strength}")
        print(f"   Бонус передач: {chemistry.passing_bonus}")
        print(f"   Бонус командной работы: {chemistry.teamwork_bonus}")
        
        # Тестируем обновление
        updated_chemistry = ChemistryCalculator.update_chemistry_interaction(
            player1, player2, 'positive'
        )
        if updated_chemistry:
            print(f"[OK] Химия обновлена, позитивных взаимодействий: {updated_chemistry.positive_interactions}")
    else:
        print("[FAIL] Не удалось создать химию")


def test_character_evolution():
    """Тестирует эволюцию характера"""
    
    # Получаем игрока с personality_traits
    player = Player.objects.filter(personality_traits__isnull=False).first()
    if not player or not player.personality_traits:
        print("[FAIL] Не найден игрок с personality_traits")
        return
    
    print(f"Тестируем эволюцию характера: {player.full_name}")
    print(f"Исходные черты: {player.personality_traits}")
    
    # Создаем матч для контекста
    match = Match.objects.first()
    if not match:
        print("[FAIL] Не найден матч для контекста")
        return
    
    # Тестируем эволюцию от забитого гола
    evolutions = EvolutionEngine.evolve_personality(
        player, 'goal_scored', match
    )
    
    if evolutions:
        print(f"[OK] Эволюция произошла:")
        for evolution in evolutions:
            print(f"   {evolution.trait_changed}: {evolution.old_value} -> {evolution.new_value} ({evolution.change_amount:+})")
        
        # Обновляем данные игрока
        player.refresh_from_db()
        print(f"   Новые черты: {player.personality_traits}")
    else:
        print("[INFO] Эволюция не произошла (случайность или отсутствие изменений)")


def test_narrative_events():
    """Тестирует создание нарративных событий"""
    
    # Получаем игроков и матч
    players = list(Player.objects.all()[:2])
    match = Match.objects.first()
    
    if len(players) < 2 or not match:
        print("[FAIL] Недостаточно данных для тестирования нарративных событий")
        return
    
    player1, player2 = players[0], players[1]
    
    # Создаем соперничество высокой интенсивности для теста
    rivalry = RivalryManager.create_rivalry(
        player1, player2, 
        rivalry_type='personal', 
        intensity='intense'
    )
    
    # Тестируем обработку события матча
    print(f"Тестируем обработку события: {player1.full_name} vs {player2.full_name}")
    
    result = NarrativeAIEngine.process_match_event(
        match, 45, 'foul', player1, player2
    )
    
    if result:
        print(f"[OK] Событие обработано:")
        
        if result['evolutions']:
            print(f"   Эволюции: {len(result['evolutions'])}")
            for evo in result['evolutions']:
                print(f"     {evo.trait_changed}: {evo.old_value} → {evo.new_value}")
        
        if result['narrative_events']:
            print(f"   Нарративные события: {len(result['narrative_events'])}")
            for event in result['narrative_events']:
                print(f"     {event.title}")
                print(f"     {event.description}")
        
        if result['updated_relationships']:
            print(f"   Обновленные отношения: {len(result['updated_relationships'])}")
    else:
        print("[INFO] Событие не сгенерировало нарративы")


def test_integration():
    """Интеграционное тестирование - полная симуляция"""
    
    # Находим активный матч или создаем тестовый
    match = Match.objects.filter(status='in_progress').first()
    
    if not match:
        # Создаем тестовый матч
        clubs = list(Club.objects.all()[:2])
        if len(clubs) < 2:
            print("[FAIL] Недостаточно клубов для создания матча")
            return
            
        match = Match.objects.create(
            home_team=clubs[0],
            away_team=clubs[1],
            status='in_progress',
            current_minute=1
        )
        print(f"[OK] Создан тестовый матч: {match}")
    
    # Инициализируем нарративы для клубов
    print("\nИнициализация нарративов для клубов...")
    
    home_narratives = NarrativeAIEngine.initialize_club_narratives(match.home_team)
    away_narratives = NarrativeAIEngine.initialize_club_narratives(match.away_team)
    
    print(f"[OK] Домашняя команда ({match.home_team.name}):")
    print(f"   Соперничества: {len(home_narratives['rivalries'])}")
    print(f"   Химия: {len(home_narratives['chemistry'])}")
    
    print(f"[OK] Гостевая команда ({match.away_team.name}):")
    print(f"   Соперничества: {len(away_narratives['rivalries'])}")
    print(f"   Химия: {len(away_narratives['chemistry'])}")
    
    # Тестируем симуляцию действий с нарративной системой
    print(f"\nТестирование симуляции с нарративной системой...")
    
    initial_events = NarrativeEvent.objects.filter(match=match).count()
    initial_evolutions = CharacterEvolution.objects.filter(match=match).count()
    
    # Симулируем несколько действий
    for i in range(5):
        try:
            result = simulate_one_action(match)
            if result and result.get('event'):
                event = result['event']
                print(f"   Минута {match.current_minute}: {event.get('event_type', 'unknown')}")
        except Exception as e:
            print(f"   [FAIL] Ошибка симуляции: {e}")
            break
    
    # Проверяем созданные нарративы
    final_events = NarrativeEvent.objects.filter(match=match).count()
    final_evolutions = CharacterEvolution.objects.filter(match=match).count()
    
    print(f"\nРезультаты симуляции:")
    print(f"   Нарративных событий создано: {final_events - initial_events}")
    print(f"   Эволюций характера: {final_evolutions - initial_evolutions}")
    
    # Показываем сводку матча
    if final_events > initial_events or final_evolutions > initial_evolutions:
        summary = NarrativeAIEngine.get_match_narrative_summary(match)
        print(f"\n[OK] Сводка нарративов матча:")
        print(f"   Всего событий: {summary['total_events']}")
        print(f"   Важных событий: {summary['major_events']}")
        print(f"   Эволюций характера: {summary['character_evolutions'].count()}")


def show_stats():
    """Показывает статистику нарративной системы"""
    
    print("\n=== СТАТИСТИКА НАРРАТИВНОЙ СИСТЕМЫ ===")
    
    rivalry_count = PlayerRivalry.objects.count()
    chemistry_count = TeamChemistry.objects.count()
    evolution_count = CharacterEvolution.objects.count()
    narrative_count = NarrativeEvent.objects.count()
    
    print(f"Соперничества: {rivalry_count}")
    print(f"Командная химия: {chemistry_count}")
    print(f"Эволюции характера: {evolution_count}")
    print(f"Нарративные события: {narrative_count}")
    
    if narrative_count > 0:
        recent_events = NarrativeEvent.objects.order_by('-timestamp')[:3]
        print(f"\nПоследние нарративные события:")
        for event in recent_events:
            print(f"  - {event.title}")


if __name__ == "__main__":
    try:
        test_narrative_system()
        show_stats()
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем.")
    except Exception as e:
        print(f"\n[FAIL] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()