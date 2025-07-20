#!/usr/bin/env python3
"""
Тестовый файл для проверки логики начала матча
Проверяет какой игрок начинает владение мячом в 1000 попытках
"""

import os
import sys
import django
from collections import defaultdict

# Настройка Django окружения
sys.path.append('/mnt/c/realfootballsim')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match
from clubs.models import Club
from players.models import Player
from matches.match_simulation import simulate_one_action


def create_test_match():
    """Создает тестовый матч с реальными данными из базы"""
    # Получаем две команды
    try:
        home_team = Club.objects.first()
        away_team = Club.objects.exclude(id=home_team.id).first()
        
        if not home_team or not away_team:
            print("Ошибка: Не найдено достаточно команд в базе данных")
            return None
            
    except Exception as e:
        print(f"Ошибка при получении команд: {e}")
        return None
    
    # Получаем реальных игроков для составов
    try:
        home_players = list(home_team.player_set.all()[:11])
        away_players = list(away_team.player_set.all()[:11])
        
        if len(home_players) < 11 or len(away_players) < 11:
            print(f"Недостаточно игроков: домашняя команда {len(home_players)}, гостевая {len(away_players)}")
            # Дополняем недостающих игроков любыми доступными
            all_players = list(Player.objects.all())
            while len(home_players) < 11 and all_players:
                player = all_players.pop(0)
                if player not in home_players and player not in away_players:
                    home_players.append(player)
            while len(away_players) < 11 and all_players:
                player = all_players.pop(0)
                if player not in home_players and player not in away_players:
                    away_players.append(player)
        
        # Создаем составы с реальными ID игроков (правильный формат для extract_player_id)
        home_lineup = {str(i): {"playerId": home_players[i].id} for i in range(min(11, len(home_players)))}
        away_lineup = {str(i): {"playerId": away_players[i].id} for i in range(min(11, len(away_players)))}
        
    except Exception as e:
        print(f"Ошибка при создании составов: {e}")
        return None
    
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
        current_player_with_ball=None,  # Специально None для тестирования логики начала
        home_lineup=home_lineup,  # Реальные составы
        away_lineup=away_lineup
    )
    
    return match


def test_match_start_logic(num_tests=1000):
    """Тестирует логику начала матча в num_tests попытках"""
    
    print(f"Запуск теста начала матча ({num_tests} попыток)...")
    
    results = {
        'home_team_starts': 0,
        'away_team_starts': 0,
        'errors': 0,
        'no_player': 0
    }
    
    starting_players = defaultdict(int)
    starting_zones = defaultdict(int)
    first_touch_results = {
        'home_goalkeeper': 0,
        'away_goalkeeper': 0,
        'other': 0,
        'errors': 0
    }
    
    for i in range(num_tests):
        try:
            # Создаем новый тестовый матч для каждой попытки
            match = create_test_match()
            if not match:
                results['errors'] += 1
                continue
            
            # Сбрасываем состояние матча
            match.current_player_with_ball = None
            match.current_zone = 'GK'
            
            # ПРОВЕРЯЕМ ПЕРВОЕ КАСАНИЕ - кто получает мяч при инициализации
            from matches.match_simulation import choose_player
            
            # Симулируем логику из simulate_one_action для первого касания
            possessing_team = match.home_team  # По логике должна быть домашняя команда
            first_player = choose_player(possessing_team, "GK", match=match)
            
            if first_player:
                # Проверяем что это действительно вратарь домашней команды
                if (first_player.club_id == match.home_team_id and 
                    first_player.position == "Goalkeeper"):
                    first_touch_results['home_goalkeeper'] += 1
                elif (first_player.club_id == match.away_team_id and 
                      first_player.position == "Goalkeeper"):
                    first_touch_results['away_goalkeeper'] += 1
                else:
                    first_touch_results['other'] += 1
            else:
                first_touch_results['errors'] += 1
            
            # Теперь выполняем полное действие для проверки итогового состояния
            action_result = simulate_one_action(match)
            
            # Отладочная информация только для первой попытки
            if i == 0:
                print(f"Отладка первой попытки:")
                print(f"  Первое касание: {first_player}")
                print(f"  Первое касание - команда: {'Домашняя' if first_player and first_player.club_id == match.home_team_id else 'Гостевая'}")
                print(f"  Результат действия: {action_result}")
                print(f"  Итоговый игрок: {match.current_player_with_ball}")
                print(f"  Итоговая зона: {match.current_zone}")
                print()
            
            # Проверяем итоговый результат (после всех действий в течение минуты)
            current_player = match.current_player_with_ball
            current_zone = match.current_zone
            
            if current_player:
                # Определяем какая команда начала
                if current_player.club_id == match.home_team_id:
                    results['home_team_starts'] += 1
                elif current_player.club_id == match.away_team_id:
                    results['away_team_starts'] += 1
                
                # Подсчитываем статистику по игрокам и зонам
                player_key = f"{current_player.first_name} {current_player.last_name} ({current_player.position})"
                starting_players[player_key] += 1
                starting_zones[current_zone] += 1
                
            else:
                results['no_player'] += 1
                
        except Exception as e:
            print(f"Ошибка в попытке {i+1}: {e}")
            results['errors'] += 1
    
    return results, starting_players, starting_zones, first_touch_results


def print_results(results, starting_players, starting_zones, first_touch_results, num_tests):
    """Выводит результаты тестирования"""
    
    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ НАЧАЛА МАТЧА ({num_tests} попыток)")
    print(f"{'='*60}")
    
    # Статистика первого касания (САМОЕ ВАЖНОЕ)
    print(f"\nПЕРВОЕ КАСАНИЕ МЯЧА (инициализация матча):")
    print(f"Вратарь домашней команды:  {first_touch_results['home_goalkeeper']} раз ({first_touch_results['home_goalkeeper']/num_tests*100:.1f}%)")
    print(f"Вратарь гостевой команды:  {first_touch_results['away_goalkeeper']} раз ({first_touch_results['away_goalkeeper']/num_tests*100:.1f}%)")
    print(f"Другой игрок:              {first_touch_results['other']} раз ({first_touch_results['other']/num_tests*100:.1f}%)")
    print(f"Ошибки первого касания:    {first_touch_results['errors']} раз ({first_touch_results['errors']/num_tests*100:.1f}%)")
    
    # Основная статистика (итоговое владение после всех действий)
    print(f"\nИТОГОВОЕ ВЛАДЕНИЕ (после всех действий в минуте):")
    print(f"Домашняя команда владеет:  {results['home_team_starts']} раз ({results['home_team_starts']/num_tests*100:.1f}%)")
    print(f"Гостевая команда владеет:  {results['away_team_starts']} раз ({results['away_team_starts']/num_tests*100:.1f}%)")
    print(f"Ошибки:                    {results['errors']} раз ({results['errors']/num_tests*100:.1f}%)")
    print(f"Нет игрока:                {results['no_player']} раз ({results['no_player']/num_tests*100:.1f}%)")
    
    # Статистика по игрокам
    if starting_players:
        print(f"\nТОП-10 ИГРОКОВ, НАЧИНАЮЩИХ МАТЧ:")
        for i, (player, count) in enumerate(sorted(starting_players.items(), key=lambda x: x[1], reverse=True)[:10]):
            print(f"{i+1:2d}. {player}: {count} раз ({count/num_tests*100:.1f}%)")
    
    # Статистика по зонам
    if starting_zones:
        print(f"\nСТАТИСТИКА ПО НАЧАЛЬНЫМ ЗОНАМ:")
        for zone, count in sorted(starting_zones.items(), key=lambda x: x[1], reverse=True):
            print(f"    {zone}: {count} раз ({count/num_tests*100:.1f}%)")


def main():
    """Главная функция"""
    
    print("Тест логики начала матча")
    print("Проверяем какой игрок начинает владение мячом")
    
    # Проверяем доступность команд и игроков
    try:
        clubs_count = Club.objects.count()
        players_count = Player.objects.count()
        
        print(f"\nВ базе данных:")
        print(f"Команд: {clubs_count}")
        print(f"Игроков: {players_count}")
        
        if clubs_count < 2:
            print("Ошибка: Нужно минимум 2 команды для тестирования")
            return
            
        if players_count < 22:
            print("Предупреждение: Мало игроков для полноценного тестирования")
    
    except Exception as e:
        print(f"Ошибка при проверке базы данных: {e}")
        return
    
    # Запускаем тест
    num_tests = 1000
    results, starting_players, starting_zones, first_touch_results = test_match_start_logic(num_tests)
    
    # Выводим результаты
    print_results(results, starting_players, starting_zones, first_touch_results, num_tests)
    
    # Анализ результатов
    print(f"\n{'='*60}")
    print("АНАЛИЗ РЕЗУЛЬТАТОВ:")
    
    # Анализ первого касания - это главное!
    if first_touch_results['home_goalkeeper'] == num_tests:
        print("✓ ОТЛИЧНО: Вратарь домашней команды ВСЕГДА начинает матч (100%)")
    elif first_touch_results['home_goalkeeper'] > num_tests * 0.95:
        print(f"✓ ХОРОШО: Вратарь домашней команды начинает в {first_touch_results['home_goalkeeper']/num_tests*100:.1f}% случаев")
    else:
        print(f"✗ ПРОБЛЕМА: Вратарь домашней команды начинает только в {first_touch_results['home_goalkeeper']/num_tests*100:.1f}% случаев")
    
    # Анализ итогового владения
    if results['home_team_starts'] > results['away_team_starts']:
        print(f"• Домашняя команда чаще владеет мячом в итоге ({results['home_team_starts']/num_tests*100:.1f}%)")
    else:
        print(f"• Гостевая команда чаще владеет мячом в итоге ({results['away_team_starts']/num_tests*100:.1f}%) - возможны перехваты")
    
    if results['errors'] > num_tests * 0.1:
        print(f"⚠ Много ошибок ({results['errors']}) - проверьте код")
    
    print(f"{'='*60}")


if __name__ == "__main__":
    main()