from scipy.stats import randint

def generate_player_stats(position):
    key_attributes = {
        'Goalkeeper': ['reflexes', 'handling', 'positioning'],
        'CenterBack': ['marking', 'tackling', 'heading'],
        'LeftBack': ['tackling', 'pace', 'crossing'],
        'RightBack': ['tackling', 'pace', 'crossing'],
        'DefensiveMidfielder': ['tackling', 'positioning', 'passing'],
        'CentralMidfielder': ['passing', 'vision', 'dribbling'],
        'AttackingMidfielder': ['dribbling', 'finishing', 'vision'],
        'LeftWinger': ['pace', 'crossing', 'dribbling'],
        'RightWinger': ['pace', 'crossing', 'dribbling'],
        'Forward': ['finishing', 'pace', 'heading']
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
        'CenterBack': {'marking': 1.2, 'tackling': 1.1, 'heading': 1.0},
        'LeftBack': {'tackling': 1.2, 'pace': 1.1, 'crossing': 1.0},
        'RightBack': {'tackling': 1.2, 'pace': 1.1, 'crossing': 1.0},
        'DefensiveMidfielder': {'tackling': 1.2, 'positioning': 1.1, 'passing': 1.0},
        'CentralMidfielder': {'passing': 1.2, 'vision': 1.1, 'dribbling': 1.0},
        'AttackingMidfielder': {'dribbling': 1.2, 'finishing': 1.1, 'vision': 1.0},
        'LeftWinger': {'pace': 1.2, 'crossing': 1.1, 'dribbling': 1.0},
        'RightWinger': {'pace': 1.2, 'crossing': 1.1, 'dribbling': 1.0},
        'Forward': {'finishing': 1.2, 'pace': 1.1, 'heading': 1.0}
    }

    for key_attr in key_attributes.get(position, []):
        stats[key_attr] = int(stats[key_attr] * weights[position][key_attr])

    return stats

# Пример вызова функции генерации игрока
goalkeeper_stats = generate_player_stats('Goalkeeper')
center_back_stats = generate_player_stats('CenterBack')
left_back_stats = generate_player_stats('LeftBack')
central_midfielder_stats = generate_player_stats('CentralMidfielder')
striker_stats = generate_player_stats('Striker')

print("Goalkeeper:", goalkeeper_stats)
print("Center Back:", center_back_stats)
print("Left Back:", left_back_stats)
print("Central Midfielder:", central_midfielder_stats)
print("Striker:", striker_stats)
