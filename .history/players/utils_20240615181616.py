from scipy.stats import randint

def generate_player_stats(position):
    key_attributes = {
        'Goalkeeper': ['reflexes', 'handling', 'positioning'],
        'Defender': ['marking', 'tackling', 'heading'],
        'Midfielder': ['passing', 'dribbling', 'vision'],
        'Forward': ['finishing', 'pace', 'dribbling']
    }
    
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

    # Применение весов к ключевым характеристикам
    weights = {
        'Goalkeeper': {'reflexes': 1.2, 'handling': 1.1, 'positioning': 1.0},
        'Defender': {'marking': 1.2, 'tackling': 1.1, 'heading': 1.0},
        'Midfielder': {'passing': 1.2, 'dribbling': 1.1, 'vision': 1.0},
        'Forward': {'finishing': 1.2, 'pace': 1.1, 'dribbling': 1.0}
    }

    for key_attr in key_attributes[position]:
        stats[key_attr] = int(stats[key_attr] * weights[position][key_attr])

    return stats

# Пример вызова функции генерации игрока
goalkeeper_stats = generate_player_stats('Goalkeeper')
print("Goalkeeper:", goalkeeper_stats)
