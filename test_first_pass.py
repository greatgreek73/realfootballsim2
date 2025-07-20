#!/usr/bin/env python3
"""
Тест первого паса от вратаря
Анализирует ТОЛЬКО первое действие (пас от вратаря к защитнику)
"""

import os
import sys
import django
import random
from collections import defaultdict

# Настройка Django окружения
sys.path.append('/mnt/c/realfootballsim')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match
from clubs.models import Club
from players.models import Player
from matches.match_simulation import choose_player, pass_success_probability, get_team_momentum, next_zone


def create_test_match():
    """Создает тестовый матч с реальными данными из базы"""
    try:
        home_team = Club.objects.first()
        away_team = Club.objects.exclude(id=home_team.id).first()
        
        if not home_team or not away_team:
            print("Ошибка: Не найдено достаточно команд")
            return None
            
        # Получаем реальных игроков для составов
        home_players = list(home_team.player_set.all()[:11])
        away_players = list(away_team.player_set.all()[:11])
        
        if len(home_players) < 11 or len(away_players) < 11:
            all_players = list(Player.objects.all())
            while len(home_players) < 11 and all_players:
                player = all_players.pop(0)
                if player not in home_players and player not in away_players:
                    home_players.append(player)
            while len(away_players) < 11 and all_players:
                player = all_players.pop(0)
                if player not in home_players and player not in away_players:
                    away_players.append(player)
        
        # Создаем составы с правильным форматом
        home_lineup = {str(i): {"playerId": home_players[i].id} for i in range(min(11, len(home_players)))}
        away_lineup = {str(i): {"playerId": away_players[i].id} for i in range(min(11, len(away_players)))}
        
        # Создаем тестовый матч
        match = Match(
            home_team=home_team,
            away_team=away_team,
            current_minute=1,
            home_score=0,
            away_score=0,
            status='live',
            current_zone='GK',
            st_shoots=0,
            st_passes=0,
            st_possessions=0,
            st_fouls=0,
            st_injury=0,
            home_momentum=0,
            away_momentum=0,
            possession_indicator=1,
            current_player_with_ball=None,
            home_lineup=home_lineup,
            away_lineup=away_lineup
        )
        
        return match
        
    except Exception as e:
        print(f"Ошибка при создании матча: {e}")
        return None


def test_first_pass_only(num_tests=1000):
    """Тестирует ТОЛЬКО первый пас от вратаря"""
    
    print(f"Тест первого паса от вратаря ({num_tests} попыток)...")
    
    results = {
        'home_gk_starts': 0,           # Вратарь домашней команды начинает
        'away_gk_starts': 0,           # Вратарь гостевой команды начинает  
        'other_starts': 0,             # Другой игрок начинает
        'no_player_error': 0,          # Ошибка - нет игрока
        'first_pass_success': 0,       # Первый пас успешен
        'first_pass_fail': 0,          # Первый пас неуспешен
        'gk_to_def_success': 0,        # Успешные пасы GK -> DEF
        'gk_to_def_fail': 0,           # Неуспешные пасы GK -> DEF
    }
    
    starting_goalkeepers = defaultdict(int)
    target_defenders = defaultdict(int)
    
    for i in range(num_tests):
        try:
            # Создаем новый матч
            match = create_test_match()
            if not match:
                results['no_player_error'] += 1
                continue
            
            # Сбрасываем состояние
            match.current_player_with_ball = None
            match.current_zone = 'GK'
            
            # ШАГИ ИЗ simulate_one_action() - ТОЛЬКО ДО ПЕРВОГО ПАСА
            
            # 1. Определяем первого игрока (должен быть вратарь домашней команды)
            possessing_team = match.home_team
            first_player = choose_player(possessing_team, "GK", match=match)
            
            if not first_player:
                results['no_player_error'] += 1
                continue
                
            # Устанавливаем первого игрока
            match.current_player_with_ball = first_player
            match.current_zone = "GK"
            
            # Проверяем кто начинает
            if (first_player.club_id == match.home_team_id and 
                first_player.position == "Goalkeeper"):
                results['home_gk_starts'] += 1
                starting_goalkeepers[f"{first_player.first_name} {first_player.last_name}"] += 1
            elif (first_player.club_id == match.away_team_id and 
                  first_player.position == "Goalkeeper"):
                results['away_gk_starts'] += 1
                starting_goalkeepers[f"{first_player.first_name} {first_player.last_name}"] += 1
            else:
                results['other_starts'] += 1
                continue
            
            # 2. Симулируем ТОЛЬКО первый пас (GK -> DEF)
            current_zone = "GK"
            target_zone = next_zone(current_zone)  # Должно быть DEF-C
            
            # Находим получателя паса
            recipient = choose_player(possessing_team, target_zone, exclude_ids={first_player.id}, match=match)
            if not recipient:
                results['no_player_error'] += 1
                continue
                
            # Находим возможного перехватчика
            opponent_team = match.away_team
            opponent = choose_player(opponent_team, target_zone, match=match)
            
            # Рассчитываем вероятность успеха паса
            pass_prob = pass_success_probability(
                first_player,      # Вратарь
                recipient,         # Защитник
                opponent,          # Соперник
                from_zone=current_zone,
                to_zone=target_zone,
                high=False,
                momentum=get_team_momentum(match, possessing_team),
            )
            
            # Проверяем успешность паса
            is_success = random.random() < pass_prob
            
            if is_success:
                results['first_pass_success'] += 1
                if target_zone.startswith('DEF'):
                    results['gk_to_def_success'] += 1
                    target_defenders[f"{recipient.first_name} {recipient.last_name} ({recipient.position})"] += 1
            else:
                results['first_pass_fail'] += 1
                if target_zone.startswith('DEF'):
                    results['gk_to_def_fail'] += 1
            
            # Отладочная информация для первых 3 попыток
            if i < 3:
                print(f"Попытка {i+1}:")
                print(f"  Первый игрок: {first_player.first_name} {first_player.last_name} ({first_player.position})")
                print(f"  Команда: {'Домашняя' if first_player.club_id == match.home_team_id else 'Гостевая'}")
                print(f"  Цель паса: {target_zone}")
                print(f"  Получатель: {recipient.first_name} {recipient.last_name} ({recipient.position})")
                print(f"  Вероятность успеха: {pass_prob:.3f}")
                print(f"  Результат: {'Успех' if is_success else 'Неудача'}")
                print()
                
        except Exception as e:
            print(f"Ошибка в попытке {i+1}: {e}")
            results['no_player_error'] += 1
    
    return results, starting_goalkeepers, target_defenders


def print_first_pass_results(results, starting_goalkeepers, target_defenders, num_tests):
    """Выводит результаты тестирования первого паса"""
    
    print(f"\n{'='*70}")
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ПЕРВОГО ПАСА ОТ ВРАТАРЯ ({num_tests} попыток)")
    print(f"{'='*70}")
    
    # Кто начинает матч
    print(f"\nКТО ДЕЛАЕТ ПЕРВЫЙ ПАС:")
    print(f"Вратарь домашней команды:  {results['home_gk_starts']} раз ({results['home_gk_starts']/num_tests*100:.1f}%)")
    print(f"Вратарь гостевой команды:  {results['away_gk_starts']} раз ({results['away_gk_starts']/num_tests*100:.1f}%)")
    print(f"Другой игрок:              {results['other_starts']} раз ({results['other_starts']/num_tests*100:.1f}%)")
    print(f"Ошибки:                    {results['no_player_error']} раз ({results['no_player_error']/num_tests*100:.1f}%)")
    
    # Успешность первого паса
    total_passes = results['first_pass_success'] + results['first_pass_fail']
    if total_passes > 0:
        print(f"\nУСПЕШНОСТЬ ПЕРВОГО ПАСА:")
        print(f"Успешные пасы:             {results['first_pass_success']} раз ({results['first_pass_success']/total_passes*100:.1f}%)")
        print(f"Неуспешные пасы:           {results['first_pass_fail']} раз ({results['first_pass_fail']/total_passes*100:.1f}%)")
        print(f"Общее количество пасов:    {total_passes}")
    
    # Статистика пасов GK -> DEF
    total_gk_def = results['gk_to_def_success'] + results['gk_to_def_fail']
    if total_gk_def > 0:
        print(f"\nПАСЫ ВРАТАРЬ -> ЗАЩИТНИК (GK -> DEF):")
        print(f"Успешные:                  {results['gk_to_def_success']} раз ({results['gk_to_def_success']/total_gk_def*100:.1f}%)")
        print(f"Неуспешные:                {results['gk_to_def_fail']} раз ({results['gk_to_def_fail']/total_gk_def*100:.1f}%)")
        print(f"Общее количество:          {total_gk_def}")
    
    # Вратари, которые начинают
    if starting_goalkeepers:
        print(f"\nВРАТАРИ, НАЧИНАЮЩИЕ МАТЧ:")
        for gk, count in sorted(starting_goalkeepers.items(), key=lambda x: x[1], reverse=True):
            print(f"  {gk}: {count} раз ({count/num_tests*100:.1f}%)")
    
    # Защитники, получающие первый пас
    if target_defenders:
        print(f"\nТОП-10 ЗАЩИТНИКОВ, ПОЛУЧАЮЩИХ ПЕРВЫЙ ПАС:")
        for i, (defender, count) in enumerate(sorted(target_defenders.items(), key=lambda x: x[1], reverse=True)[:10]):
            print(f"{i+1:2d}. {defender}: {count} раз ({count/results['gk_to_def_success']*100:.1f}% от успешных)")


def main():
    """Главная функция"""
    
    print("Тест первого паса от вратаря")
    print("Анализ ТОЛЬКО первого действия в матче")
    
    # Проверяем доступность данных
    try:
        clubs_count = Club.objects.count()
        players_count = Player.objects.count()
        
        print(f"\nВ базе данных:")
        print(f"Команд: {clubs_count}")
        print(f"Игроков: {players_count}")
        
        if clubs_count < 2:
            print("Ошибка: Нужно минимум 2 команды")
            return
            
    except Exception as e:
        print(f"Ошибка при проверке базы данных: {e}")
        return
    
    # Запускаем тест
    num_tests = 1000
    results, starting_goalkeepers, target_defenders = test_first_pass_only(num_tests)
    
    # Выводим результаты
    print_first_pass_results(results, starting_goalkeepers, target_defenders, num_tests)
    
    # Анализ
    print(f"\n{'='*70}")
    print("АНАЛИЗ РЕЗУЛЬТАТОВ:")
    
    if results['home_gk_starts'] == num_tests:
        print("✓ ОТЛИЧНО: Вратарь домашней команды ВСЕГДА делает первый пас (100%)")
    elif results['home_gk_starts'] > num_tests * 0.95:
        print(f"✓ ХОРОШО: Вратарь домашней команды делает первый пас в {results['home_gk_starts']/num_tests*100:.1f}% случаев")
    else:
        print(f"✗ ПРОБЛЕМА: Вратарь домашней команды делает первый пас только в {results['home_gk_starts']/num_tests*100:.1f}% случаев")
    
    total_passes = results['first_pass_success'] + results['first_pass_fail']
    if total_passes > 0:
        success_rate = results['first_pass_success'] / total_passes * 100
        if success_rate >= 85:
            print(f"✓ ХОРОШО: Высокая успешность первого паса ({success_rate:.1f}%)")
        elif success_rate >= 70:
            print(f"~ СРЕДНЕ: Средняя успешность первого паса ({success_rate:.1f}%)")
        else:
            print(f"✗ НИЗКО: Низкая успешность первого паса ({success_rate:.1f}%)")
    
    print(f"{'='*70}")


if __name__ == "__main__":
    main()