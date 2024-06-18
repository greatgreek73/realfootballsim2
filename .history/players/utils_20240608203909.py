from scipy.stats import randint

def generate_player_stats(position):
    if position == 'Goalkeeper':
        attributes = [
            'strength', 'stamina', 'pace', 'positioning', 
            'handling', 'reflexes', 'aerial', 'jumping', 
            'command', 'throwing', 'kicking'
        ]
        total_points = 200
    else:
        attributes = [
            'strength', 'stamina', 'pace', 'marking', 'tackling', 'work_rate', 
            'positioning', 'passing', 'crossing', 'dribbling', 'ball_control', 
            'heading', 'finishing', 'long_range', 'vision'
        ]
        total_points = 400

    num_attributes = len(attributes)
    points = [randint.rvs(1, total_points // num_attributes) for _ in range(num_attributes)]
    scale_factor = total_points / sum(points)
    points = [int(point * scale_factor) for point in points]

    # Корректируем значения, чтобы сумма точно равнялась total_points
    current_total = sum(points)
    if current_total < total_points:
        points[-1] += total_points - current_total
    elif current_total > total_points:
        points[-1] -= current_total - total_points

    stats = {attributes[i]: points[i] for i in range(num_attributes)}
    return stats
