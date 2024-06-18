from scipy.stats import norm

def generate_player_stats(position):
    key_attributes = {
        'Goalkeeper': ['reflexes', 'handling', 'positioning'],
        'Right Back': ['tackling', 'pace', 'crossing'],
        'Left Back': ['tackling', 'pace', 'crossing'],
        'Center Back': ['marking', 'tackling', 'heading'],
        'Defensive Midfielder': ['tackling', 'positioning', 'passing'],
        'Left Defensive Midfielder': ['tackling', 'positioning', 'passing'],
        'Right Defensive Midfielder': ['tackling', 'positioning', 'passing'],
        'Right Midfielder': ['crossing', 'pace', 'dribbling'],
        'Central Midfielder': ['passing', 'vision', 'dribbling'],
        'Left Midfielder': ['crossing', 'pace', 'dribbling'],
        'Attacking Midfielder': ['dribbling', 'finishing', 'vision'],
        'Center Forward': ['finishing', 'pace', 'heading']
    }

    weights = {
        'Goalkeeper': {'reflexes': 0.3, 'handling': 0.2, 'positioning': 0.1},
        'Right Back': {'tackling': 0.3, 'pace': 0.2, 'crossing': 0.1},
        'Left Back': {'tackling': 0.3, 'pace': 0.2, 'crossing': 0.1},
        'Center Back': {'marking': 0.3, 'tackling': 0.2, 'heading': 0.1},
        'Defensive Midfielder': {'tackling': 0.3, 'positioning': 0.2, 'passing': 0.1},
        'Left Defensive Midfielder': {'tackling': 0.3, 'positioning': 0.2, 'passing': 0.1},
        'Right Defensive Midfielder': {'tackling': 0.3, 'positioning': 0.2, 'passing': 0.1},
        'Right Midfielder': {'crossing': 0.3, 'pace': 0.2, 'dribbling': 0.1},
        'Central Midfielder': {'passing': 0.3, 'vision': 0.2, 'dribbling': 0.1},
        'Left Midfielder': {'crossing': 0.3, 'pace': 0.2, 'dribbling': 0.1},
        'Attacking Midfielder': {'dribbling': 0.3, 'finishing': 0.2, 'vision': 0.1},
        'Center Forward': {'finishing': 0.3, 'pace': 0.2, 'heading': 0.1}
    }

    mu, sigma = 70, 15

    stats = {
        'strength': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'stamina': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'pace': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'marking': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'tackling': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'work_rate': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'positioning': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'passing': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'crossing': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'dribbling': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'ball_control': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'heading': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'finishing': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'long_range': max(1, min(100, int(norm.rvs(mu, sigma)))),
        'vision': max(1, min(100, int(norm.rvs(mu, sigma)))),
    }

    for attribute in key_attributes[position]:
        stats[attribute] = max(1, min(100, int(norm.rvs(mu, sigma) * weights[position][attribute])))

    if position == 'Goalkeeper':
        stats.update({
            'reflexes': max(1, min(100, int(norm.rvs(mu, sigma) * weights[position]['reflexes']))),
            'handling': max(1, min(100, int(norm.rvs(mu, sigma) * weights[position]['handling']))),
            'aerial': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'jumping': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'command': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'throwing': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'kicking': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'strength': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'stamina': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'pace': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'positioning': max(1, min(100, int(norm.rvs(mu, sigma)))),
        })

    return stats