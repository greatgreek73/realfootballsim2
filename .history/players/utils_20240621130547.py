from scipy.stats import norm
import random

# Constants
POSITIONS = {
    'Goalkeeper': {
        'key_attributes': ['reflexes', 'handling', 'positioning'],
        'weights': [
            ({'reflexes': 3.3, 'handling': 3.2, 'positioning': 3.1}, 0.40),
            ({'reflexes': 2.3, 'handling': 2.2, 'positioning': 2.1}, 0.35),
            ({'reflexes': 1.3, 'handling': 1.2, 'positioning': 1.1}, 0.25)
        ]
    },
    'Right Back': {
        'key_attributes': ['tackling', 'marking', 'crossing'],
        'weights': [
            ({'tackling': 2.3, 'marking': 2.2, 'crossing': 2.1}, 0.40),
            ({'tackling': 1.3, 'marking': 1.2, 'crossing': 3.1}, 0.35),
            ({'tackling': 3.3, 'marking': 1.2, 'crossing': 1.1}, 0.25)
        ]
    },
    'Left Back': {
        'key_attributes': ['tackling', 'marking', 'crossing'],
        'weights': [
            ({'tackling': 2.3, 'marking': 2.2, 'crossing': 2.1}, 0.40),
            ({'tackling': 1.3, 'marking': 1.2, 'crossing': 3.1}, 0.35),
            ({'tackling': 3.3, 'marking': 1.2, 'crossing': 1.1}, 0.25)
        ]
    },
    'Center Back': {
        'key_attributes': ['marking', 'tackling', 'heading'],
        'weights': [
            ({'marking': 3.3, 'tackling': 2.2, 'heading': 1.1}, 0.40),
            ({'marking': 2.3, 'tackling': 3.2, 'heading': 1.1}, 0.35),
            ({'marking': 2.3, 'tackling': 2.2, 'heading': 2.1}, 0.25)
        ]
    },
    'Defensive Midfielder': {
        'key_attributes': ['tackling', 'marking', 'passing'],
        'weights': [
            ({'tackling': 3.3, 'marking': 2.2, 'passing': 1.1}, 0.40),
            ({'tackling': 2.3, 'marking': 3.2, 'passing': 1.1}, 0.35),
            ({'tackling': 2.3, 'marking': 2.2, 'passing': 2.1}, 0.25)
        ]
    },
    'Left Defensive Midfielder': {
        'key_attributes': ['tackling', 'marking', 'crossing'],
        'weights': [
            ({'tackling': 2.3, 'marking': 2.2, 'crossing': 2.1}, 0.40),
            ({'tackling': 3.3, 'marking': 1.2, 'crossing': 2.1}, 0.35),
            ({'tackling': 1.3, 'marking': 3.2, 'crossing': 2.1}, 0.25)
        ]
    },
    'Right Defensive Midfielder': {
        'key_attributes': ['tackling', 'marking', 'crossing'],
        'weights': [
            ({'tackling': 2.3, 'marking': 2.2, 'crossing': 2.1}, 0.40),
            ({'tackling': 3.3, 'marking': 1.2, 'crossing': 2.1}, 0.35),
            ({'tackling': 1.3, 'marking': 3.2, 'crossing': 2.1}, 0.25)
        ]
    },
    'Right Midfielder': {
        'key_attributes': ['crossing', 'pace', 'dribbling'],
        'weights': [
            ({'crossing': 3.3, 'pace': 2.2, 'dribbling': 1.1}, 0.40),
            ({'crossing': 2.3, 'pace': 3.2, 'dribbling': 1.1}, 0.35),
            ({'crossing': 2.3, 'pace': 2.2, 'dribbling': 2.1}, 0.25)
        ]
    },
    'Central Midfielder': {
        'key_attributes': ['passing', 'vision', 'work_rate'],
        'weights': [
            ({'passing': 3.3, 'vision': 2.2, 'work_rate': 1.1}, 0.40),
            ({'passing': 2.3, 'vision': 3.2, 'work_rate': 1.1}, 0.35),
            ({'passing': 2.3, 'vision': 2.2, 'work_rate': 2.1}, 0.25)
        ]
    },
    'Left Midfielder': {
        'key_attributes': ['crossing', 'pace', 'dribbling'],
        'weights': [
            ({'crossing': 3.3, 'pace': 2.2, 'dribbling': 1.1}, 0.40),
            ({'crossing': 2.3, 'pace': 3.2, 'dribbling': 1.1}, 0.35),
            ({'crossing': 2.3, 'pace': 2.2, 'dribbling': 2.1}, 0.25)
        ]
    },
    'Attacking Midfielder': {
        'key_attributes': ['dribbling', 'finishing', 'vision'],
        'weights': [
            ({'dribbling': 3.3, 'finishing': 2.2, 'vision': 1.1}, 0.40),
            ({'dribbling': 2.3, 'finishing': 3.2, 'vision': 1.1}, 0.35),
            ({'dribbling': 2.3, 'finishing': 2.2, 'vision': 2.1}, 0.25)
        ]
    },
    'Center Forward': {
        'key_attributes': ['finishing', 'long_range', 'heading'],
        'weights': [
            ({'finishing': 3.3, 'long_range': 2.2, 'heading': 1.1}, 0.40),
            ({'finishing': 2.3, 'long_range': 3.2, 'heading': 1.1}, 0.35),
            ({'finishing': 2.3, 'long_range': 2.2, 'heading': 2.1}, 0.25)
        ]
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

def select_weights(position):
    weights_options = POSITIONS[position]['weights']
    return random.choices(
        [option[0] for option in weights_options],
        weights=[option[1] for option in weights_options]
    )[0]

def generate_stat(mu=50, sigma=10, weight=1):
    return max(1, min(100, int(norm.rvs(mu, sigma) * weight)))

def generate_base_stats():
    return {attr: generate_stat() for attr in BASE_ATTRIBUTES}

def generate_position_specific_stats(position):
    weights = select_weights(position)
    return {
        attr: generate_stat(weight=weights.get(attr, 1))
        for attr in POSITIONS[position]['key_attributes']
    }

def generate_goalkeeper_stats():
    weights = select_weights('Goalkeeper')
    gk_stats = {}
    for attr in GOALKEEPER_ATTRIBUTES:
        if attr in weights:
            gk_stats[attr] = generate_stat(weight=weights[attr])
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