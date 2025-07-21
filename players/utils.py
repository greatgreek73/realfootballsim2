from scipy.stats import norm
import random
import sys
import os

def generate_stat(weight=1):
    """Генерирует базовую характеристику"""
    base_value = norm.rvs(50, 10)
    weighted_value = base_value * weight
    return max(1, min(99, int(weighted_value)))

def generate_player_stats(position, player_class):
    """Генерирует характеристики игрока в зависимости от позиции"""
    # Базовые характеристики
    morale_value = generate_stat()
    base_stats = {
        'strength': generate_stat(),
        'stamina': generate_stat(),
        'morale': morale_value,
        'base_morale': morale_value,  # Базовая мораль равна начальной
        'pace': generate_stat(),
        'positioning': generate_stat(),
    }

    if position == 'Goalkeeper':
        # Характеристики вратаря (8 дополнительных характеристик)
        gk_stats = {
            'reflexes': generate_stat(),
            'handling': generate_stat(),
            'aerial': generate_stat(),
            'command': generate_stat(),
            'distribution': generate_stat(),
            'one_on_one': generate_stat(),
            'rebound_control': generate_stat(),
            'shot_reading': generate_stat()
        }
        stats = {**base_stats, **gk_stats}
    else:
        # Характеристики полевого игрока (12 дополнительных характеристик)
        field_stats = {
            'marking': generate_stat(),
            'tackling': generate_stat(),
            'work_rate': generate_stat(),
            'passing': generate_stat(),
            'crossing': generate_stat(),
            'dribbling': generate_stat(),
            'flair': generate_stat(),
            'heading': generate_stat(),
            'finishing': generate_stat(),
            'long_range': generate_stat(),
            'vision': generate_stat(),
            'accuracy': generate_stat()
        }
        stats = {**base_stats, **field_stats}

        # Прежний словарь для различных позиций
        position_modifiers = {
            'Center Back': {
                'marking': 1.2, 'tackling': 1.2, 'heading': 1.1,
                'strength': 1.1, 'finishing': 0.8, 'dribbling': 0.8
            },
            'Right Back': {
                'pace': 1.1, 'crossing': 1.1, 'stamina': 1.1,
                'tackling': 1.1, 'marking': 1.1
            },
            'Left Back': {
                'pace': 1.1, 'crossing': 1.1, 'stamina': 1.1,
                'tackling': 1.1, 'marking': 1.1
            },
            # Новый ключ для левого полузащитника:
            'Left Midfielder': {
                # Примерные бонусы: фланговому полузащитнику полезнее скорость, дриблинг и кроссы
                'pace': 1.2,
                'crossing': 1.2,
                'dribbling': 1.1,
                'work_rate': 1.1,
                'stamina': 1.1
            },
            # Исходная логика для "Central Midfielder"
            'Central Midfielder': {
                'passing': 1.2,
                'vision': 1.2,
                'work_rate': 1.1,
                'stamina': 1.1,
                'positioning': 1.1
            },
            'Center Forward': {
                'finishing': 1.3, 'heading': 1.2, 'positioning': 1.2,
                'strength': 1.1, 'dribbling': 1.1
            }
        }

        # Применяем модификаторы для соответствующей позиции
        if position in position_modifiers:
            for attr, mod in position_modifiers[position].items():
                if attr in stats:
                    stats[attr] = min(99, int(stats[attr] * mod))

    # Модификатор класса игрока (чем выше player_class, тем выше бонус)
    class_modifier = (5 - player_class) * 0.1
    for key in stats:
        stats[key] = min(99, int(stats[key] * (1 + class_modifier)))

    return stats

def print_player_stats(stats):
    """Вспомогательная функция для вывода характеристик"""
    print("\nХарактеристики игрока:")
    total = 0
    count = 0
    for attr, value in sorted(stats.items()):
        print(f"{attr}: {value}")
        total += value
        count += 1
    if count > 0:
        print(f"\nСредний рейтинг: {total/count:.1f}")
