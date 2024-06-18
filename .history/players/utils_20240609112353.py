import numpy as np
from scipy.stats import dirichlet

def generate_player_stats(position):
    if position == 'Goalkeeper':
        total_points = 200
        num_stats = 11
    else:
        total_points = 400
        num_stats = 15

    # Генерация значений характеристик с использованием распределения Дирихле
    stats_values = dirichlet.rvs([1] * num_stats)[0] * total_points
    stats_values = np.round(stats_values).astype(int)

    # Убедитесь, что каждое значение находится в пределах от 1 до 100
    for i in range(num_stats):
        if stats_values[i] < 1:
            stats_values[i] = 1
        elif stats_values[i] > 100:
            stats_values[i] = 100

    if position == 'Goalkeeper':
        stats = {
            'strength': stats_values[0],
            'stamina': stats_values[1],
            'pace': stats_values[2],
            'positioning': stats_values[3],
            'reflexes': stats_values[4],
            'handling': stats_values[5],
            'aerial': stats_values[6],
            'jumping': stats_values[7],
            'command': stats_values[8],
            'throwing': stats_values[9],
            'kicking': stats_values[10],
        }
    else:
        stats = {
            'strength': stats_values[0],
            'stamina': stats_values[1],
            'pace': stats_values[2],
            'marking': stats_values[3],
            'tackling': stats_values[4],
            'work_rate': stats_values[5],
            'positioning': stats_values[6],
            'passing': stats_values[7],
            'crossing': stats_values[8],
            'dribbling': stats_values[9],
            'ball_control': stats_values[10],
            'heading': stats_values[11],
            'finishing': stats_values[12],
            'long_range': stats_values[13],
            'vision': stats_values[14],
        }

    return stats
