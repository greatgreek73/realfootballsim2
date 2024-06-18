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
            'strength': 10,
            'stamina': 10,
            'pace': 10,
            'positioning': 10,
            'reflexes': 10,
            'handling': 10,
            'aerial': 10,
            'jumping': 10,
            'command': 10,
            'throwing': 10,
            'kicking': 10
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

    for stat in stats_means:
        value = int(norm.rvs(stats_means[stat], stats_stds[stat]))
        stats[stat] = max(1, min(100, value))  # Ensure values are within [1, 100]

    return stats
