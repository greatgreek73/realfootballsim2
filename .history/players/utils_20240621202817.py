from scipy.stats import norm
import random

# Constants
POSITIONS = {
    'Goalkeeper': {
        'attributes': {
            'reflexes': [(3.3, 0.40), (2.3, 0.35), (1.3, 0.25)],
            'handling': [(3.2, 0.40), (2.2, 0.35), (1.2, 0.25)],
            'positioning': [(3.1, 0.40), (2.1, 0.35), (1.1, 0.25)],
            'aerial': [(1.0, 1.0)],
            'jumping': [(1.0, 1.0)],
            'command': [(1.0, 1.0)],
            'throwing': [(1.0, 1.0)],
            'kicking': [(1.0, 1.0)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'pace': [(1.0, 1.0)]
        }
    },
    'Right Back': {
        'attributes': {
            'tackling': [(2.3, 0.40), (1.3, 0.35), (3.3, 0.25)],
            'marking': [(2.2, 0.40), (1.2, 0.35), (1.2, 0.25)],
            'crossing': [(2.1, 0.40), (3.1, 0.35), (1.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'pace': [(1.0, 1.0)],
            'work_rate': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'passing': [(1.0, 1.0)],
            'dribbling': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'heading': [(1.0, 1.0)],
            'finishing': [(1.0, 1.0)],
            'long_range': [(1.0, 1.0)],
            'vision': [(1.0, 1.0)]
        }
    },
    'Left Back': {
        'attributes': {
            'tackling': [(2.3, 0.40), (1.3, 0.35), (3.3, 0.25)],
            'marking': [(2.2, 0.40), (1.2, 0.35), (1.2, 0.25)],
            'crossing': [(2.1, 0.40), (3.1, 0.35), (1.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'pace': [(1.0, 1.0)],
            'work_rate': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'passing': [(1.0, 1.0)],
            'dribbling': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'heading': [(1.0, 1.0)],
            'finishing': [(1.0, 1.0)],
            'long_range': [(1.0, 1.0)],
            'vision': [(1.0, 1.0)]
        }
    },
    'Center Back': {
        'attributes': {
            'marking': [(3.3, 0.40), (2.3, 0.35), (2.3, 0.25)],
            'tackling': [(2.2, 0.40), (3.2, 0.35), (2.2, 0.25)],
            'heading': [(1.1, 0.40), (1.1, 0.35), (2.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'pace': [(1.0, 1.0)],
            'work_rate': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'passing': [(1.0, 1.0)],
            'dribbling': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'crossing': [(1.0, 1.0)],
            'finishing': [(1.0, 1.0)],
            'long_range': [(1.0, 1.0)],
            'vision': [(1.0, 1.0)]
        }
    },
    'Defensive Midfielder': {
        'attributes': {
            'tackling': [(3.3, 0.40), (2.3, 0.35), (2.3, 0.25)],
            'marking': [(2.2, 0.40), (3.2, 0.35), (2.2, 0.25)],
            'passing': [(1.1, 0.40), (1.1, 0.35), (2.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'pace': [(1.0, 1.0)],
            'work_rate': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'crossing': [(1.0, 1.0)],
            'dribbling': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'heading': [(1.0, 1.0)],
            'finishing': [(1.0, 1.0)],
            'long_range': [(1.0, 1.0)],
            'vision': [(1.0, 1.0)]
        }
    },
    'Central Midfielder': {
        'attributes': {
            'passing': [(3.3, 0.40), (2.3, 0.35), (2.3, 0.25)],
            'vision': [(2.2, 0.40), (3.2, 0.35), (2.2, 0.25)],
            'work_rate': [(1.1, 0.40), (1.1, 0.35), (2.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'pace': [(1.0, 1.0)],
            'marking': [(1.0, 1.0)],
            'tackling': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'crossing': [(1.0, 1.0)],
            'dribbling': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'heading': [(1.0, 1.0)],
            'finishing': [(1.0, 1.0)],
            'long_range': [(1.0, 1.0)]
        }
    },
    'Right Midfielder': {
        'attributes': {
            'crossing': [(3.3, 0.40), (2.3, 0.35), (2.3, 0.25)],
            'pace': [(2.2, 0.40), (3.2, 0.35), (2.2, 0.25)],
            'dribbling': [(1.1, 0.40), (1.1, 0.35), (2.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'marking': [(1.0, 1.0)],
            'tackling': [(1.0, 1.0)],
            'work_rate': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'passing': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'heading': [(1.0, 1.0)],
            'finishing': [(1.0, 1.0)],
            'long_range': [(1.0, 1.0)],
            'vision': [(1.0, 1.0)]
        }
    },
    'Left Midfielder': {
        'attributes': {
            'crossing': [(3.3, 0.40), (2.3, 0.35), (2.3, 0.25)],
            'pace': [(2.2, 0.40), (3.2, 0.35), (2.2, 0.25)],
            'dribbling': [(1.1, 0.40), (1.1, 0.35), (2.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'marking': [(1.0, 1.0)],
            'tackling': [(1.0, 1.0)],
            'work_rate': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'passing': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'heading': [(1.0, 1.0)],
            'finishing': [(1.0, 1.0)],
            'long_range': [(1.0, 1.0)],
            'vision': [(1.0, 1.0)]
        }
    },
    'Attacking Midfielder': {
        'attributes': {
            'dribbling': [(3.3, 0.40), (2.3, 0.35), (2.3, 0.25)],
            'finishing': [(2.2, 0.40), (3.2, 0.35), (2.2, 0.25)],
            'vision': [(1.1, 0.40), (1.1, 0.35), (2.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'pace': [(1.0, 1.0)],
            'marking': [(1.0, 1.0)],
            'tackling': [(1.0, 1.0)],
            'work_rate': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'passing': [(1.0, 1.0)],
            'crossing': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'heading': [(1.0, 1.0)],
            'long_range': [(1.0, 1.0)]
        }
    },
    'Center Forward': {
        'attributes': {
            'finishing': [(3.3, 0.40), (2.3, 0.35), (2.3, 0.25)],
            'long_range': [(2.2, 0.40), (3.2, 0.35), (2.2, 0.25)],
            'heading': [(1.1, 0.40), (1.1, 0.35), (2.1, 0.25)],
            'strength': [(1.0, 1.0)],
            'stamina': [(1.0, 1.0)],
            'pace': [(1.0, 1.0)],
            'marking': [(1.0, 1.0)],
            'tackling': [(1.0, 1.0)],
            'work_rate': [(1.0, 1.0)],
            'positioning': [(1.0, 1.0)],
            'passing': [(1.0, 1.0)],
            'crossing': [(1.0, 1.0)],
            'dribbling': [(1.0, 1.0)],
            'ball_control': [(1.0, 1.0)],
            'vision': [(1.0, 1.0)]
        }
    }
}

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
    for attr in ALL_ATTRIBUTES:
        if attr in POSITIONS[position]['attributes']:
            weight = select_weight(POSITIONS[position]['attributes'][attr])
            stats[attr] = generate_stat(weight=weight)
        else:
            stats[attr] = generate_stat()
    
    return adjust_stats_for_class(stats, player_class)

def adjust_stats_for_class(stats, player_class):
    total = sum(stats.values())
    min_total, max_total = CLASS_RANGES[player_class]
    
    if total < min_total or total > max_total:
        scale_factor = random.uniform(min_total, max_total) / total
        return {attr: max(1, min(100, int(value * scale_factor))) for attr, value in stats.items()}
    return stats