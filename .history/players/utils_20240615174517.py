import numpy as np
from scipy.stats import randint

def generate_gaussian_stat(mean, std_dev):
    return max(1, min(100, int(np.random.normal(mean, std_dev))))

def apply_correlations(stats, correlation_matrix):
    correlated_stats = np.dot(correlation_matrix, list(stats.values()))
    return {stat: max(1, min(100, int(value))) for stat, value in zip(stats.keys(), correlated_stats)}

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size), 'valid') / window_size

def generate_player_stats(position):
    key_attributes = {
        'Goalkeeper': ['reflexes', 'handling', 'positioning', 'strength', 'stamina', 'pace', 'aerial', 'jumping', 'command', 'throwing', 'kicking'],
        'Defender': ['marking', 'tackling', 'heading', 'strength', 'stamina', 'pace'],
        'Midfielder': ['passing', 'dribbling', 'vision', 'strength', 'stamina', 'pace'],
        'Forward': ['finishing', 'pace', 'dribbling', 'strength', 'stamina', 'heading']
    }

    weights = {
        'Goalkeeper': {'reflexes': 1.0, 'handling': 0.9, 'positioning': 0.8, 'strength': 0.7, 'stamina': 0.6, 'pace': 0.5, 'aerial': 0.8, 'jumping': 0.8, 'command': 0.7, 'throwing': 0.6, 'kicking': 0.6},
        'Defender': {'marking': 1.0, 'tackling': 1.0, 'heading': 0.9, 'strength': 0.8, 'stamina': 0.7, 'pace': 0.6},
        'Midfielder': {'passing': 1.0, 'dribbling': 0.9, 'vision': 0.8, 'strength': 0.7, 'stamina': 0.8, 'pace': 0.7},
        'Forward': {'finishing': 1.0, 'pace': 0.9, 'dribbling': 0.8, 'strength': 0.7, 'stamina': 0.7, 'heading': 0.6}
    }

    mean = 50
    std_dev = 20

    base_stats = {stat: generate_gaussian_stat(mean, std_dev) for stat in key_attributes[position]}

    weighted_stats = {stat: int(value * weights[position].get(stat, 1)) for stat, value in base_stats.items()}

    correlation_matrix = np.identity(len(weighted_stats))
    correlated_stats = apply_correlations(weighted_stats, correlation_matrix)

    smoothed_stats_values = moving_average(list(correlated_stats.values()), window_size=3)
    smoothed_stats = {stat: value for stat, value in zip(correlated_stats.keys(), smoothed_stats_values)}

    return smoothed_stats

# Пример генерации игроков для каждой позиции
goalkeeper_stats = generate_player_stats('Goalkeeper')
defender_stats = generate_player_stats('Defender')
midfielder_stats = generate_player_stats('Midfielder')
forward_stats = generate_player_stats('Forward')

print("Goalkeeper:", goalkeeper_stats)
print("Defender:", defender_stats)
print("Midfielder:", midfielder_stats)
print("Forward:", forward_stats)
