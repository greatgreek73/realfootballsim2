from scipy.stats import randint

def generate_player_stats(position):
    if position == 'Goalkeeper':
        target_sum = 200
        num_stats = 11  # количество параметров для вратарей
    else:
        target_sum = 400
        num_stats = 15  # количество параметров для полевых игроков

    stats_values = [randint.rvs(1, 101) for _ in range(num_stats)]
    total_sum = sum(stats_values)

    normalization_factor = target_sum / total_sum
    normalized_stats_values = [int(value * normalization_factor) for value in stats_values]

    if position == 'Goalkeeper':
        stats = {
            'strength': normalized_stats_values[0],
            'stamina': normalized_stats_values[1],
            'pace': normalized_stats_values[2],
            'positioning': normalized_stats_values[3],
            'reflexes': normalized_stats_values[4],
            'handling': normalized_stats_values[5],
            'aerial': normalized_stats_values[6],
            'jumping': normalized_stats_values[7],
            'command': normalized_stats_values[8],
            'throwing': normalized_stats_values[9],
            'kicking': normalized_stats_values[10],
        }
    else:
        stats = {
            'strength': normalized_stats_values[0],
            'stamina': normalized_stats_values[1],
            'pace': normalized_stats_values[2],
            'marking': normalized_stats_values[3],
            'tackling': normalized_stats_values[4],
            'work_rate': normalized_stats_values[5],
            'positioning': normalized_stats_values[6],
            'passing': normalized_stats_values[7],
            'crossing': normalized_stats_values[8],
            'dribbling': normalized_stats_values[9],
            'ball_control': normalized_stats_values[10],
            'heading': normalized_stats_values[11],
            'finishing': normalized_stats_values[12],
            'long_range': normalized_stats_values[13],
            'vision': normalized_stats_values[14],
        }

    return stats