#!/usr/bin/env python3
"""
Тест первого паса от вратаря для конкретного клуба Hereford United (ID 321)
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
from matches.match_simulation import choose_player, pass_success_probability, get_team_momentum, next_zone, zone_prefix, clamp


def debug_pass_probability_detailed(
    passer: Player,
    recipient: Player,
    opponent: Player | None,
    *,
    from_zone: str,
    to_zone: str,
    high: bool = False,
    momentum: int = 0,
) -> dict:
    """Детальный анализ каждого компонента формулы вероятности паса"""
    
    f_prefix = zone_prefix(from_zone)
    t_prefix = zone_prefix(to_zone)
    
    # 1. Базовая вероятность
    def_base = 0.6
    if f_prefix == "GK" and t_prefix == "DEF":
        def_base = 0.9
    elif f_prefix == "DEF" and t_prefix == "DM":
        def_base = 0.8
    elif f_prefix == "DM" and t_prefix == "MID":
        def_base = 0.75
    elif f_prefix == "MID" and t_prefix == "AM":
        def_base = 0.7
    elif f_prefix == "AM" and t_prefix == "FWD":
        def_base = 0.65
    base = def_base
    
    # 2. Бонусы
    bonus = (passer.passing + passer.vision) / 200
    rec_bonus = recipient.positioning / 200 if recipient else 0
    heading_bonus = recipient.heading / 200 if high and recipient else 0
    
    # 3. Штрафы от соперника
    penalty = 0
    if opponent:
        penalty = (opponent.marking + opponent.tackling) / 400
    
    # 4. Множители
    stamina_factor = passer.stamina / 100
    morale_factor = 0.5 + passer.morale / 200
    momentum_factor = 1 + momentum / 200
    
    # Итоговая вероятность
    raw_probability = (base + bonus + rec_bonus + heading_bonus - penalty) * stamina_factor * morale_factor * momentum_factor
    final_probability = clamp(raw_probability)
    
    return {
        'from_zone': from_zone,
        'to_zone': to_zone,
        'base_probability': def_base,
        'adjusted_base': base,
        'passer_bonus': bonus,
        'recipient_bonus': rec_bonus,
        'heading_bonus': heading_bonus,
        'opponent_penalty': penalty,
        'stamina_factor': stamina_factor,
        'morale_factor': morale_factor,
        'momentum_factor': momentum_factor,
        'raw_probability': raw_probability,
        'final_probability': final_probability,
        'passer_stats': {
            'passing': passer.passing,
            'vision': passer.vision,
            'stamina': passer.stamina,
            'morale': passer.morale,
            'distribution': getattr(passer, 'distribution', None),  # Вратарская характеристика
        },
        'recipient_stats': {
            'positioning': recipient.positioning if recipient else None,
            'heading': recipient.heading if recipient else None,
        },
        'opponent_stats': {
            'marking': opponent.marking if opponent else None,
            'tackling': opponent.tackling if opponent else None,
        }
    }


def test_hereford_united():
    """Тестирует первый пас для Hereford United"""
    
    print("ТЕСТ ПЕРВОГО ПАСА ДЛЯ HEREFORD UNITED (ID 321)")
    print("=" * 60)
    
    try:
        # Получаем Hereford United
        home_team = Club.objects.get(id=321)
        print(f"Домашняя команда: {home_team.name}")
        
        # Получаем другую команду как соперника
        away_team = Club.objects.exclude(id=321).first()
        print(f"Гостевая команда: {away_team.name}")
        
    except Club.DoesNotExist:
        print("❌ Клуб Hereford United (ID 321) не найден!")
        return
    except Exception as e:
        print(f"❌ Ошибка при получении команд: {e}")
        return
    
    # Получаем игроков Hereford United
    home_players = list(home_team.player_set.all())
    away_players = list(away_team.player_set.all()[:11])
    
    print(f"\nИгроков в Hereford United: {len(home_players)}")
    print(f"Игроков в {away_team.name}: {len(away_players)}")
    
    # Получаем вратарей Hereford United
    hereford_goalkeepers = home_team.player_set.filter(position="Goalkeeper")
    print(f"\nВратарей в Hereford United: {hereford_goalkeepers.count()}")
    
    if not hereford_goalkeepers:
        print("❌ Вратари не найдены в Hereford United!")
        return
    
    # Показываем всех вратарей
    print("\nВРАТАРИ HEREFORD UNITED:")
    for i, gk in enumerate(hereford_goalkeepers):
        print(f"{i+1}. {gk.first_name} {gk.last_name}")
        print(f"   ПАС: {gk.passing}")
        print(f"   ВИДЕНИЕ: {gk.vision}")
        print(f"   ВЫНОСЛИВОСТЬ: {gk.stamina}")
        print(f"   МОРАЛЬ: {gk.morale}")
        print(f"   РАСПРЕДЕЛЕНИЕ: {gk.distribution}")
        print(f"   ПОЗИЦИОНИРОВАНИЕ: {gk.positioning}")
        print()
    
    # Создаем составы с реальными игроками
    if len(home_players) >= 11:
        home_lineup = {str(i): {"playerId": home_players[i].id} for i in range(11)}
    else:
        print(f"❌ Недостаточно игроков в Hereford United: {len(home_players)}")
        return
        
    if len(away_players) >= 11:
        away_lineup = {str(i): {"playerId": away_players[i].id} for i in range(11)}
    else:
        print(f"❌ Недостаточно игроков в {away_team.name}: {len(away_players)}")
        return
    
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
    
    # Тестируем первый пас
    print("=" * 60)
    print("АНАЛИЗ ПЕРВОГО ПАСА")
    print("=" * 60)
    
    # Получаем первого игрока (вратаря)
    goalkeeper = choose_player(home_team, "GK", match=match)
    if not goalkeeper:
        print("❌ Не удалось выбрать вратаря через choose_player")
        return
    
    print(f"ВЫБРАННЫЙ ВРАТАРЬ: {goalkeeper.first_name} {goalkeeper.last_name}")
    print(f"Команда: {goalkeeper.club.name}")
    print(f"Позиция: {goalkeeper.position}")
    
    # Цель паса
    target_zone = next_zone("GK")  # DEF-C
    defender = choose_player(home_team, target_zone, exclude_ids={goalkeeper.id}, match=match)
    
    if not defender:
        print(f"❌ Не найден защитник для зоны {target_zone}")
        return
    
    print(f"\nПОЛУЧАТЕЛЬ ПАСА: {defender.first_name} {defender.last_name}")
    print(f"Позиция: {defender.position}")
    
    # Соперник
    opponent = choose_player(away_team, target_zone, match=match)
    if opponent:
        print(f"\nСОПЕРНИК: {opponent.first_name} {opponent.last_name} ({away_team.name})")
        print(f"Позиция: {opponent.position}")
    else:
        print(f"\nСОПЕРНИК: НЕТ")
    
    # Анализируем вероятность
    analysis = debug_pass_probability_detailed(
        goalkeeper,
        defender,
        opponent,
        from_zone="GK",
        to_zone=target_zone,
        high=False,
        momentum=0
    )
    
    print(f"\n" + "=" * 60)
    print("ДЕТАЛЬНЫЙ РАСЧЕТ ВЕРОЯТНОСТИ")
    print("=" * 60)
    
    print(f"Маршрут: {analysis['from_zone']} -> {analysis['to_zone']}")
    print(f"1. Базовая вероятность: {analysis['base_probability']:.3f} (90% для GK->DEF)")
    print(f"2. Бонус пасующего: +{analysis['passer_bonus']:.3f} (пас={analysis['passer_stats']['passing']} + видение={analysis['passer_stats']['vision']})/200")
    print(f"3. Бонус получателя: +{analysis['recipient_bonus']:.3f} (позиционирование={analysis['recipient_stats']['positioning']})/200")
    print(f"4. Штраф от соперника: -{analysis['opponent_penalty']:.3f}")
    if opponent:
        print(f"   (опека={analysis['opponent_stats']['marking']} + отбор={analysis['opponent_stats']['tackling']})/400")
    print(f"5. Множитель выносливости: x{analysis['stamina_factor']:.3f} (выносливость={analysis['passer_stats']['stamina']})")
    print(f"6. Множитель морали: x{analysis['morale_factor']:.3f} (0.5 + мораль={analysis['passer_stats']['morale']}/200)")
    print(f"7. Множитель моментума: x{analysis['momentum_factor']:.3f}")
    
    print(f"\nИТОГОВАЯ ВЕРОЯТНОСТЬ: {analysis['final_probability']:.3f} ({analysis['final_probability']*100:.1f}%)")
    
    # Тестируем несколько попыток
    print(f"\n" + "=" * 60)
    print("ТЕСТ НЕСКОЛЬКИХ ПОПЫТОК (100 раз)")
    print("=" * 60)
    
    successes = 0
    total_attempts = 100
    
    for i in range(total_attempts):
        is_success = random.random() < analysis['final_probability']
        if is_success:
            successes += 1
    
    success_rate = successes / total_attempts * 100
    print(f"Успешных пасов: {successes}/{total_attempts} ({success_rate:.1f}%)")
    print(f"Ожидаемая вероятность: {analysis['final_probability']*100:.1f}%")
    print(f"Отклонение: {abs(success_rate - analysis['final_probability']*100):.1f}%")


if __name__ == "__main__":
    test_hereford_united()