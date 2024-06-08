from scipy.stats import randint

def generate_player_stats(position):
    # Генерация случайных характеристик от 1 до 100
    stats = {
        'strength': randint.rvs(1, 101),
        'stamina': randint.rvs(1, 101),
        'pace': randint.rvs(1, 101),
        'marking': randint.rvs(1, 101),
        'tackling': randint.rvs(1, 101),
        'work_rate': randint.rvs(1, 101),
        'positioning': randint.rvs(1, 101),
        'passing': randint.rvs(1, 101),
        'crossing': randint.rvs(1, 101),
        'dribbling': randint.rvs(1, 101),
        'ball_control': randint.rvs(1, 101),
        'heading': randint.rvs(1, 101),
        'finishing': randint.rvs(1, 101),
        'long_range': randint.rvs(1, 101),
        'vision': randint.rvs(1, 101),
    }

    if position == 'Goalkeeper':
        stats.update({
            'strength': randint.rvs(1, 101),
            'stamina': randint.rvs(1, 101),
            'pace': randint.rvs(1, 101),
            'positioning': randint.rvs(1, 101),
            'reflexes': randint.rvs(1, 101),
            'handling': randint.rvs(1, 101),
            'aerial': randint.rvs(1, 101),
            'jumping': randint.rvs(1, 101),
            'command': randint.rvs(1, 101),
            'throwing': randint.rvs(1, 101),
            'kicking': randint.rvs(1, 101),
        })

    return stats
