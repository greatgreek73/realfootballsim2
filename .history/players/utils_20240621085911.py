from scipy.stats import norm
import random

# Constants
POSITIONS = {
    'Goalkeeper': {
        'key_attributes': ['reflexes', 'handling', 'positioning'],
        'weights': {'reflexes': 3.3, 'handling': 3.2, 'positioning': 3.1}
    },
    'Right Back': {
        'key_attributes': ['tackling', 'marking', 'crossing'],
        'weights': {'tackling': 1.3, 'marking': 1.2, 'crossing': 2.1}
    },
    'Left Back': {
        'key_attributes': ['tackling', 'marking', 'crossing'],
        'weights': {'tackling': 1.3, 'marking': 1.2, 'crossing': 2.1}
    },
    'Center Back': {
        'key_attributes': ['marking', 'tackling', 'heading'],
        'weights': {'marking': 1.3, 'tackling': 1.2, 'heading': 2.1}
    },
    'Defensive Midfielder': {
        'key_attributes': ['tackling', 'marking', 'passing'],
        'weights': {'tackling': 1.3, 'marking': 1.2, 'passing': 2.1}
    },
    'Left Defensive Midfielder': {
        'key_attributes': ['tackling', 'marking', 'crossing'],
        'weights': {'tackling': 1.3, 'marking': 1.2, 'crossing': 2.1}
    },
    'Right Defensive Midfielder': {
        'key_attributes': ['tackling', 'marking', 'crossing'],
        'weights': {'tackling': 1.3, 'marking': 1.2, 'crossing': 2.1}
    },
    'Right Midfielder': {
        'key_attributes': ['crossing', 'pace', 'dribbling'],
        'weights': {'crossing': 1.3, 'pace': 1.2, 'dribbling': 2.1}
    },
    'Central Midfielder': {
        'key_attributes': ['passing', 'vision', 'work_rate'],
        'weights': {'passing': 1.3, 'vision': 1.2, 'work_rate': 2.1}
    },
    'Left Midfielder': {
        'key_attributes': ['crossing', 'pace', 'dribbling'],
        'weights': {'crossing': 3.3, 'pace': 3.2, 'dribbling': 2.1}
    },
    'Attacking Midfielder': {
        'key_attributes': ['dribbling', 'finishing', 'vision'],
        'weights': {'dribbling': 1.3, 'finishing': 1.2, 'vision': 2.1}
    },
    'Center Forward': {
        'key_attributes': ['finishing', 'long_range', 'heading'],
        'weights': {'finishing': 2.3, 'long_range': 2.2, 'heading': 2.1}
    }
}

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

def generate_stat(mu=50, sigma=10, weight=1):
    return max(1, min(100, int(norm.rvs(mu, sigma) * weight)))

def generate_base_stats():
    return {attr: generate_stat() for attr in BASE_ATTRIBUTES}

def generate_position_specific_stats(position):
    return {
        attr: generate_stat(weight=POSITIONS[position]['weights'].get(attr, 1))
        for attr in POSITIONS[position]['key_attributes']
    }

def generate_goalkeeper_stats():
    gk_stats = {}
    for attr in GOALKEEPER_ATTRIBUTES:
        if attr in POSITIONS['Goalkeeper']['weights']:
            gk_stats[attr] = generate_stat(weight=POSITIONS['Goalkeeper']['weights'][attr])
        else:
            gk_stats[attr] = generate_stat()
    return gk_stats

def adjust_stats_for_class(stats, player_class):
    total = sum(stats.values())
    min_total, max_total = CLASS_RANGES[player_class]
    
    if total < min_total or total > max_total:
        scale_factor = random.uniform(min_total, max_total) / total
        return {attr: max(1, min(100, int(value * scale_factor))) for attr, value in stats.items()}
    return stats

def generate_player_stats(position, player_class):
    if position == 'Goalkeeper':
        stats = generate_goalkeeper_stats()
    else:
        stats = generate_base_stats()
        stats.update(generate_position_specific_stats(position))
    
    return adjust_stats_for_class(stats, player_class)