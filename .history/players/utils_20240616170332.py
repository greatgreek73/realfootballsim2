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

    # Генерация характеристик с использованием нормального распределения
    # Среднее значение (mu) и стандартное отклонение (sigma)
    mu, sigma = 20, 15

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

    if position == 'Goalkeeper':
        stats.update({
            'reflexes': max(1, min(100, int(norm.rvs(mu, sigma)))),
            'handling': max(1, min(100, int(norm.rvs(mu, sigma)))),
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
