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
    return max(1, min(100, int(norm.rvs(mu, sigma) * weight)))

def generate_player_stats(position, player_class):
    stats = {}
    position_weights = POSITIONS_WEIGHTS[player_class][position]['attributes']
    
    for attr in ALL_ATTRIBUTES:
        if attr in position_weights:
            weight = select_weight(position_weights[attr])
            stats[attr] = generate_stat(weight=weight)
        else:
            stats[attr] = generate_stat()
    
    return adjust_stats_for_class(stats, player_class)

def adjust_stats_for_class(stats, player_class):
    total = sum(stats.values())
    min_total, max_total = CLASS_RANGES[player_class]
    
    if total < min_total or total > max_total:
        target_total = random.uniform(min_total, max_total)
        scale_factor = target_total / total
        
        # Масштабируем все характеристики
        scaled_stats = {attr: value * scale_factor for attr, value in stats.items()}
        
        # Округляем значения и убеждаемся, что они в пределах от 1 до 100
        adjusted_stats = {attr: max(1, min(100, round(value))) for attr, value in scaled_stats.items()}
        
        # Проверяем, что сумма после округления все еще в нужном диапазоне
        adjusted_total = sum(adjusted_stats.values())
        if adjusted_total < min_total or adjusted_total > max_total:
            # Если нет, добавляем или вычитаем по 1 из случайных характеристик
            diff = int(target_total - adjusted_total)
            attributes = list(adjusted_stats.keys())
            random.shuffle(attributes)
            for attr in attributes:
                if diff > 0:
                    if adjusted_stats[attr] < 100:
                        adjusted_stats[attr] += 1
                        diff -= 1
                elif diff < 0:
                    if adjusted_stats[attr] > 1:
                        adjusted_stats[attr] -= 1
                        diff += 1
                if diff == 0:
                    break
        
        return adjusted_stats
    return stats