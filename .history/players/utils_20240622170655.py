from scipy.stats import norm
import random
import sys
import os

# Добавляем текущую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from player_attributes_config import POSITIONS_WEIGHTS

# Constants
ALL_ATTRIBUTES = [
    'strength', 'stamina', 'pace', 'marking', 'tackling', 'work_rate',
    'positioning', 'passing', 'crossing', 'dribbling', 'ball_control',
    'heading', 'finishing', 'long_range', 'vision', 'reflexes', 'handling',
    'aerial', 'jumping', 'command', 'throwing', 'kicking'
]

CLASS_RANGES = {
    1: (550, 590),
    2: (470, 490),
    3: (380, 400),
    4: (290, 320)
}

def select_weight(attribute_weights):
    weights, probabilities = zip(*attribute_weights)
    return random.choices(weights, probabilities)[0]

def generate_stat(mu=50, sigma=10, weight=1):
    return max(1, min(100, int(norm.rvs(mu, sigma))))

def generate_player_stats(position, player_class):
    stats = {}
    position_weights = POSITIONS_WEIGHTS[player_class][position]['attributes']
    
    for attr in ALL_ATTRIBUTES:
        if attr in position_weights:
            weight = select_weight(position_weights[attr])
            stats[attr] = generate_stat(mu=50*weight, sigma=10*weight)
        else:
            stats[attr] = generate_stat()
    
    return adjust_stats_for_class(stats, player_class)

def adjust_stats_for_class(stats, player_class):
    total = sum(stats.values())
    min_total, max_total = CLASS_RANGES[player_class]
    
    if total < min_total:
        scale_factor = min_total / total
        stats = {attr: max(1, min(100, int(value * scale_factor))) for attr, value in stats.items()}
    elif total > max_total:
        scale_factor = max_total / total
        stats = {attr: max(1, min(100, int(value * scale_factor))) for attr, value in stats.items()}
    
    # Убедимся, что сумма точно попадает в диапазон
    while sum(stats.values()) < min_total:
        attr = random.choice(list(stats.keys()))
        if stats[attr] < 100:
            stats[attr] += 1
    while sum(stats.values()) > max_total:
        attr = random.choice(list(stats.keys()))
        if stats[attr] > 1:
            stats[attr] -= 1
    
    return stats