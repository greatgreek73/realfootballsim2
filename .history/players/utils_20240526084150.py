import numpy as np

def generate_player_stats(position):
    # Генерация случайных характеристик от 1 до 100
    stats = {
        'strength': np.random.randint(1, 101),
        'stamina': np.random.randint(1, 101),
        'pace': np.random.randint(1, 101),
        'marking': np.random.randint(1, 101),
        'tackling': np.random.randint(1, 101),
        'work_rate': np.random.randint(1, 101),
        'positioning': np.random.randint(1, 101),
        'passing': np.random.randint(1, 101),
        'crossing': np.random.randint(1, 101),
        'dribbling': np.random.randint(1, 101),
        'ball_control': np.random.randint(1, 101),
        'heading': np.random.randint(1, 101),
        'finishing': np.random.randint(1, 101),
        'long_range': np.random.randint(1, 101),
        'vision': np.random.randint(1, 101),
    }

    if position == 'Goalkeeper':
        stats.update({
            'handling': np.random.randint(1, 101),
            'reflexes': np.random.randint(1, 101),
            'aerial': np.random.randint(1, 101),
            'jumping': np.random.randint(1, 101),
            'command': np.random.randint(1, 101),
            'throwing': np.random.randint(1, 101),
            'kicking': np.random.randint(1, 101),
        })

    return stats
