#!/usr/bin/env python3
"""
Диагностика вероятности первого паса от вратаря
Анализирует каждый компонент формулы pass_success_probability()
"""

import os
import sys
import django

# Настройка Django окружения
sys.path.append('/mnt/c/realfootballsim')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match
from clubs.models import Club
from players.models import Player
from matches.match_simulation import choose_player, zone_prefix, get_team_momentum, next_zone, clamp


def debug_pass_probability(
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
    
    # 2. Штраф за дальность (для высоких пасов)
    distance_penalty = 0
    if high:
        ROW_INDEX = {"GK": 0, "DEF": 1, "DM": 2, "MID": 3, "AM": 4, "FWD": 5}
        try:
            distance = ROW_INDEX[t_prefix] - ROW_INDEX[f_prefix]
        except Exception:
            distance = 1
        distance_penalty = 0.05 * max(distance - 1, 0)
        base -= distance_penalty
    
    # 3. Бонусы
    bonus = (passer.passing + passer.vision) / 200
    rec_bonus = recipient.positioning / 200 if recipient else 0
    heading_bonus = recipient.heading / 200 if high and recipient else 0
    
    # 4. Штрафы от соперника
    penalty = 0
    if opponent:
        penalty = (opponent.marking + opponent.tackling) / 400
    
    # 5. Множители
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
        'distance_penalty': distance_penalty,
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


def create_test_match():
    """Создает тестовый матч для анализа"""
    try:
        home_team = Club.objects.first()
        away_team = Club.objects.exclude(id=home_team.id).first()
        
        home_players = list(home_team.player_set.all()[:11])
        away_players = list(away_team.player_set.all()[:11])
        
        if len(home_players) < 11:
            all_players = list(Player.objects.all())
            while len(home_players) < 11 and all_players:
                player = all_players.pop(0)
                if player not in home_players and player not in away_players:
                    home_players.append(player)
        
        home_lineup = {str(i): {"playerId": home_players[i].id} for i in range(min(11, len(home_players)))}
        away_lineup = {str(i): {"playerId": away_players[i].id} for i in range(min(11, len(away_players)))}
        
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


def analyze_first_pass_probability():
    """Анализирует вероятность первого паса от вратаря"""
    
    print("ДИАГНОСТИКА ВЕРОЯТНОСТИ ПЕРВОГО ПАСА ОТ ВРАТАРЯ")
    print("=" * 60)
    
    # Создаем тестовый матч
    match = create_test_match()
    if not match:
        print("Ошибка создания матча")
        return
    
    # Получаем участников первого паса
    possessing_team = match.home_team
    opponent_team = match.away_team
    
    # Вратарь (пасующий)
    goalkeeper = choose_player(possessing_team, "GK", match=match)
    if not goalkeeper:
        print("Не найден вратарь")
        return
    
    # Защитник (получатель)
    current_zone = "GK"
    target_zone = next_zone(current_zone)  # DEF-C
    defender = choose_player(possessing_team, target_zone, exclude_ids={goalkeeper.id}, match=match)
    if not defender:
        print("Не найден защитник")
        return
    
    # Соперник (перехватчик)
    opponent = choose_player(opponent_team, target_zone, match=match)
    
    # Моментум
    momentum = get_team_momentum(match, possessing_team)
    
    # Анализируем вероятность
    analysis = debug_pass_probability(
        goalkeeper,
        defender,
        opponent,
        from_zone=current_zone,
        to_zone=target_zone,
        high=False,
        momentum=momentum
    )
    
    # Выводим результаты
    print(f"\nУЧАСТНИКИ ПАСА:")
    print(f"Пасующий (вратарь): {goalkeeper.first_name} {goalkeeper.last_name}")
    print(f"  Пас: {analysis['passer_stats']['passing']}")
    print(f"  Видение: {analysis['passer_stats']['vision']}")
    print(f"  Выносливость: {analysis['passer_stats']['stamina']}")
    print(f"  Мораль: {analysis['passer_stats']['morale']}")
    
    print(f"\nПолучатель (защитник): {defender.first_name} {defender.last_name}")
    print(f"  Позиционирование: {analysis['recipient_stats']['positioning']}")
    print(f"  Игра головой: {analysis['recipient_stats']['heading']}")
    
    if opponent:
        print(f"\nСоперник (перехватчик): {opponent.first_name} {opponent.last_name}")
        print(f"  Опека: {analysis['opponent_stats']['marking']}")
        print(f"  Отбор: {analysis['opponent_stats']['tackling']}")
    else:
        print(f"\nСоперник: НЕТ")
    
    print(f"\nДЕТАЛЬНЫЙ РАСЧЕТ:")
    print(f"Маршрут: {analysis['from_zone']} -> {analysis['to_zone']}")
    print(f"1. Базовая вероятность: {analysis['base_probability']:.3f} (90% для GK->DEF)")
    print(f"2. Штраф за дальность: -{analysis['distance_penalty']:.3f}")
    print(f"3. Скорректированная база: {analysis['adjusted_base']:.3f}")
    print(f"4. Бонус пасующего: +{analysis['passer_bonus']:.3f} (пас+видение)/200")
    print(f"5. Бонус получателя: +{analysis['recipient_bonus']:.3f} (позиционирование/200)")
    print(f"6. Бонус за игру головой: +{analysis['heading_bonus']:.3f}")
    print(f"7. Штраф от соперника: -{analysis['opponent_penalty']:.3f} (опека+отбор)/400")
    print(f"8. Множитель выносливости: ×{analysis['stamina_factor']:.3f}")
    print(f"9. Множитель морали: ×{analysis['morale_factor']:.3f}")
    print(f"10. Множитель моментума: ×{analysis['momentum_factor']:.3f}")
    
    print(f"\nИТОГ:")
    print(f"Сырая вероятность: {analysis['raw_probability']:.3f}")
    print(f"Итоговая вероятность: {analysis['final_probability']:.3f} ({analysis['final_probability']*100:.1f}%)")
    
    # Анализ проблем
    print(f"\nАНАЛИЗ ПРОБЛЕМ:")
    
    if analysis['opponent_penalty'] > 0.2:
        print(f"🔴 ПРОБЛЕМА: Слишком большой штраф от соперника ({analysis['opponent_penalty']:.3f})")
        print(f"   Опека соперника: {analysis['opponent_stats']['marking']}")
        print(f"   Отбор соперника: {analysis['opponent_stats']['tackling']}")
    
    if analysis['passer_bonus'] < 0.3:
        print(f"🔴 ПРОБЛЕМА: Низкий бонус пасующего ({analysis['passer_bonus']:.3f})")
        print(f"   Пас вратаря: {analysis['passer_stats']['passing']}")
        print(f"   Видение вратаря: {analysis['passer_stats']['vision']}")
    
    if analysis['stamina_factor'] < 0.8:
        print(f"🔴 ПРОБЛЕМА: Низкая выносливость ({analysis['stamina_factor']:.3f})")
        print(f"   Выносливость вратаря: {analysis['passer_stats']['stamina']}")
    
    if analysis['morale_factor'] < 0.8:
        print(f"🔴 ПРОБЛЕМА: Низкая мораль ({analysis['morale_factor']:.3f})")
        print(f"   Мораль вратаря: {analysis['passer_stats']['morale']}")
    
    # Анализируем несколько случаев
    print(f"\n" + "="*60)
    print("АНАЛИЗ НЕСКОЛЬКИХ СЛУЧАЙНЫХ ПАСОВ:")
    
    for i in range(3):
        print(f"\nСлучай {i+1}:")
        
        # Новые игроки
        gk = choose_player(possessing_team, "GK", match=match)
        df = choose_player(possessing_team, target_zone, exclude_ids={gk.id}, match=match)
        op = choose_player(opponent_team, target_zone, match=match)
        
        if gk and df:
            analysis = debug_pass_probability(gk, df, op, from_zone="GK", to_zone="DEF-C", momentum=0)
            print(f"  {gk.last_name} -> {df.last_name}")
            print(f"  Соперник: {op.last_name if op else 'НЕТ'}")
            print(f"  Итоговая вероятность: {analysis['final_probability']:.3f} ({analysis['final_probability']*100:.1f}%)")
            print(f"  Штраф от соперника: {analysis['opponent_penalty']:.3f}")


if __name__ == "__main__":
    analyze_first_pass_probability()