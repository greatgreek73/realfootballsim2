import numpy as np

def generate_player_stats(position):
    if position == 'Goalkeeper':
        total_points = 200
        num_stats = 11
        weights = [0.3, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]  # weights for each stat
    elif position == 'Defender':
        total_points = 300
        num_stats = 12
        weights = [0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    elif position == 'Midfielder':
        total_points = 350
        num_stats = 13
        weights = [0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    elif position == 'Forward':
        total_points = 400
        num_stats = 14
        weights = [0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

    stats_values = np.random.dirichlet(np.ones(num_stats), 1)[0] * total_points
    stats_values = np.round(stats_values).astype(int)

    # Apply weights to each stat
    for i in range(num_stats):
        stats_values[i] *= weights[i]

    # Ensure each stat is within the range [1, 100]
    for i in range(num_stats):
        if stats_values[i] < 1:
            stats_values[i] = 1
        elif stats_values[i] > 100:
            stats_values[i] = 100

    # Create a dictionary with the stats
    stats = {}
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
    elif position == 'Defender':
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
        }
    elif position == 'Midfielder':
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
            'vision': stats_values[12],
        }
    elif position == 'Forward':
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
        }

    return stats