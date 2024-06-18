from scipy.stats import norm

def generate_player_stats(position):
    stats = {}

    if position == 'Goalkeeper':
        stats_means = {
            'strength': 25,
            'stamina': 30,
            'pace': 20,
            'positioning': 50,
            'reflexes': 90,
            'handling': 75,
            'aerial': 45,
            'jumping': 70,
            'command': 15,
            'throwing': 30,
            'kicking': 35
        }
        stats_stds = {
            'strength': 40,
            'stamina': 40,
            'pace': 40,
            'positioning': 40,
            'reflexes': 40,
            'handling': 40,
            'aerial': 40,
            'jumping': 40,
            'command': 40,
            'throwing': 40,
            'kicking': 40
        }
    else:
        stats_means = {
            'strength': 50,
            'stamina': 60,
            'pace': 70,
            'marking': 50,
            'tackling': 55,
            'work_rate': 60,
            'positioning': 65,
            'passing': 70,
            'crossing': 60,
            'dribbling': 75,
            'ball_control': 70,
            'heading': 55,
            'finishing': 65,
            'long_range': 60,
            'vision': 65
        }
        stats_stds = {
            'strength': 10,
            'stamina': 10,
            'pace': 10,
            'marking': 10,
            'tackling': 10,
            'work_rate': 10,
            'positioning': 10,
            'passing': 10,
            'crossing': 10,
            'dribbling': 10,
            'ball_control': 10,
            'heading': 10,
            'finishing': 10,
            'long_range': 10,
            'vision': 10
        }

    # Генерируем случайные значения характеристик
    raw_stats = {}
    for stat in stats_means:
        value = int(norm.rvs(stats_means[stat], stats_stds[stat]))
        raw_stats[stat] = max(1, min(100, value))

    # Нормализуем значения характеристик, чтобы сумма равнялась 500
    total = sum(raw_stats.values())
    stats_points = [int((raw_stats[stat] / total) * 500) for stat in raw_stats]
    remaining_points = 500 - sum(stats_points)

    # Распределяем оставшиеся очки между характеристиками
    while remaining_points > 0:
        for i, stat in enumerate(raw_stats):
            if remaining_points > 0:
                stats_points[i] += 1
                remaining_points -= 1
            else:
                break

    stats = {stat: points for stat, points in zip(raw_stats, stats_points)}
    return stats