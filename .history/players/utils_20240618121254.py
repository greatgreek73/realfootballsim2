from scipy.stats import norm

def generate_player_stats(position):
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

    mu, sigma = 50, 10

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
            'positioning': max(1, min(100, int(norm.rvs(mu, sigma) * weights[position]['positioning']))),
        })

    return stats