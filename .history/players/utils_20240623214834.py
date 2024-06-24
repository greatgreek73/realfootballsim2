from scipy.stats import norm
import random
import sys
import os

# Добавляем текущую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from player_attributes_config import POSITIONS_WEIGHTS

# Constants
BASE_ATTRIBUTES = [
    'strength', 'stamina', 'pace', 'marking', 'tackling', 'work_rate',
    'positioning', 'passing', 'crossing', 'dribbling', 'ball_control',
    'heading', 'finishing', 'long_range', 'vision'
]

GOALKEEPER_ATTRIBUTES = [
    'reflexes', 'handling', 'aerial', 'jumping', 'command', 'throwing',
    'kicking', 'strength', 'stamina', 'pace', 'positioning'
]

CLASS_RANGES = {
    1: (550, 590),
    2: (470, 490),
    3: (380, 400),
    4: (290, 320)
}

def select_weight(attribute_weights):
    weights, probabilities = zip(*attribute_weights)
    selected = random.choices(weights, probabilities)[0]
    print(f"select_weight called with: {attribute_weights}")
    print(f"Selected weight: {selected}")
    return selected

def generate_stat(weight=1):
    return max(1, min(100, int(norm.rvs(50, 10))))

def generate_player_stats(position, player_class):
    stats = {}
    position_weights = POSITIONS_WEIGHTS[player_class][position]['attributes']
    
    print(f"\nGenerating stats for {position}, class {player_class}")
    
    if position == 'Goalkeeper':
        attributes = GOALKEEPER_ATTRIBUTES
    else:
        attributes = BASE_ATTRIBUTES
    
    for attr in attributes:
        if attr in position_weights:
            weight = select_weight(position_weights[attr])
            stat = generate_stat(weight)
            print(f"{attr}: weight = {weight}, stat = {stat}")
        else:
            stat = generate_stat()
            print(f"{attr}: no weight, stat = {stat}")
        stats[attr] = stat
    
    print(f"Initial total: {sum(stats.values())}")
    return adjust_stats_for_class(stats, player_class)

def adjust_stats_for_class(stats, player_class):
    total = sum(stats.values())
    min_total, max_total = CLASS_RANGES[player_class]
    target_total = random.randint(min_total, max_total)
    
    print(f"Adjusting stats. Initial total: {total}, Target total: {target_total}")
    
    while total != target_total:
        if total < target_total:
            attr = random.choice([a for a in stats if stats[a] < 100])
            stats[attr] += 1
            total += 1
        else:
            attr = random.choice([a for a in stats if stats[a] > 1])
            stats[attr] -= 1
            total -= 1
    
    print(f"Final total: {total}")
    return stats

def print_player_stats(stats):
    total = sum(stats.values())
    print(f"Total sum of attributes: {total}")
    for attr, value in sorted(stats.items()):
        print(f"{attr}: {value}")

if __name__ == "__main__":
    # Тест функции select_weight
    test_weights = [(1.0, 0.40), (1.0, 0.35), (1.0, 0.25)]
    print("Testing select_weight function:")
    for _ in range(10):
        select_weight(test_weights)
    
    print("\nGenerating a test goalkeeper:")
    gk_stats = generate_player_stats('Goalkeeper', 1)
    print("\nFinal goalkeeper stats:")
    print_player_stats(gk_stats)
    
    print("\nGenerating a test outfield player:")
    player_stats = generate_player_stats('Center Forward', 1)
    print("\nFinal outfield player stats:")
    print_player_stats(player_stats)

    # Тест генерации статистики
    print("\nTest stat generation:")
    test_values = [generate_stat() for _ in range(1000)]
    print(f"Average: {sum(test_values) / len(test_values)}")
    print(f"Min: {min(test_values)}")
    print(f"Max: {max(test_values)}")