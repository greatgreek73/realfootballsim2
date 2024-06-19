import random
from scipy.stats import norm

def generate_player_stats(position, player_class):
    key_attributes = {
        'Goalkeeper': ['reflexes', 'handling', 'positioning'],
        'Right Back': ['tackling', 'marking', 'crossing'],
        'Left Back': ['tackling', 'marking', 'crossing'],
        'Center Back': ['marking', 'tackling', 'heading'],
        'Defensive Midfielder': ['tackling', 'marking', 'passing'],
        'Left Defensive Midfielder': ['tackling', 'marking', 'crossing'],
        'Right Defensive Midfielder': ['tackling', 'marking', 'crossing'],
        'Right Midfielder': ['crossing', 'pace', 'dribbling'],
        'Central Midfielder': ['passing', 'vision', 'work_rate'],
        'Left Midfielder': ['crossing', 'pace', 'dribbling'],
        'Attacking Midfielder': ['dribbling', 'finishing', 'vision'],
        'Center Forward': ['finishing', 'long_range', 'heading']
    }

    weights = {
        'Goalkeeper': {'reflexes': 3.3, 'handling': 3.2, 'positioning': 3.1},
        'Right Back': {'tackling': 1.3, 'marking': 1.2, 'crossing': 2.1},
        'Left Back': {'tackling': 1.3, 'marking': 1.2, 'crossing': 2.1},
        'Center Back': {'marking': 1.3, 'tackling': 1.2, 'heading': 2.1},
        'Defensive Midfielder': {'tackling': 1.3, 'marking': 1.2, 'passing': 2.1},
        'Left Defensive Midfielder': {'tackling': 1.3, 'marking': 1.2, 'crossing': 2.1},
        'Right Defensive Midfielder': {'tackling': 1.3, 'marking': 1.2, 'crossing': 2.1},
        'Right Midfielder': {'crossing': 1.3, 'pace': 1.2, 'dribbling': 2.1},
        'Central Midfielder': {'passing': 1.3, 'vision': 1.2, 'work_rate': 2.1},
        'Left Midfielder': {'crossing': 3.3, 'pace': 3.2, 'dribbling': 2.1},
        'Attacking Midfielder': {'dribbling': 1.3, 'finishing': 1.2, 'vision': 2.1},
        'Center Forward': {'finishing': 2.3, 'long_range': 2.2, 'heading': 2.1}
    }

    class_ranges = {
        1: (550, 590),
        2: (470, 490),
        3: (360, 390),
        4: (290, 310)
    }

    min_range, max_range = class_ranges[player_class]

    attributes = {}
    for attribute in key_attributes[position]:
        value = random.randint(min_range, max_range) / len(key_attributes[position])
        attributes[attribute] = value

    total_attributes = sum(attributes.values())
    normalization_factor = (min_range + max_range) / 2 / total_attributes
    for attribute, value in attributes.items():
        attributes[attribute] = int(value * normalization_factor)

    return attributes