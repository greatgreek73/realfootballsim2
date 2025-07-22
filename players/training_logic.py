import random
from typing import Dict, List, Tuple
from .models import Player
from .training import TrainingSettings


def get_or_create_training_settings(player: Player) -> TrainingSettings:
    """Получает или создает настройки тренировок для игрока."""
    settings, created = TrainingSettings.objects.get_or_create(
        player=player
    )
    return settings


def calculate_training_points(player: Player) -> int:
    """
    Вычисляет базовое количество очков для тренировки игрока.
    Базовое количество: 3 очка за тренировку.
    """
    base_points = 3
    
    # Модификатор возраста  
    age_modifier = player.get_age_training_modifier()
    
    # Бонус расцвета
    bloom_bonus = player.get_bloom_bonus()
    
    # Итоговые очки с учетом всех модификаторов
    total_points = base_points * age_modifier
    
    if player.is_in_bloom:
        total_points += base_points * bloom_bonus
    
    # Минимум 1 очко (даже для старых игроков)
    # Для отрицательного эффекта используется отдельная логика
    return max(1, int(total_points))


def distribute_training_points(player: Player, total_points: int) -> Dict[str, int]:
    """
    Распределяет очки тренировки между группами характеристик
    согласно настройкам игрока.
    """
    settings = get_or_create_training_settings(player)
    distribution = {}
    
    if player.is_goalkeeper:
        # Используем группы вратаря
        weights = settings.get_goalkeeper_weights()
        groups = Player.GOALKEEPER_GROUPS
    else:
        # Используем группы полевого игрока
        weights = settings.get_field_player_weights()
        groups = Player.FIELD_PLAYER_GROUPS
    
    # Распределяем очки по группам согласно весам
    remaining_points = total_points
    
    for group_name, group_attrs in groups.items():
        if group_name in weights:
            # Вычисляем количество очков для этой группы
            group_points = int(total_points * weights[group_name])
            
            if group_points > 0:
                # Распределяем очки внутри группы между атрибутами
                attrs_count = len(group_attrs)
                base_per_attr = group_points // attrs_count
                extra_points = group_points % attrs_count
                
                for i, attr_name in enumerate(group_attrs):
                    # Базовые очки + возможно 1 дополнительное очко
                    attr_points = base_per_attr + (1 if i < extra_points else 0)
                    
                    if attr_name not in distribution:
                        distribution[attr_name] = 0
                    distribution[attr_name] += attr_points
                    
                remaining_points -= group_points
    
    # Если остались очки из-за округления, распределяем их случайно
    if remaining_points > 0:
        all_attrs = []
        for group_attrs in groups.values():
            all_attrs.extend(group_attrs)
        
        for _ in range(remaining_points):
            random_attr = random.choice(all_attrs)
            if random_attr not in distribution:
                distribution[random_attr] = 0
            distribution[random_attr] += 1
    
    return distribution


def apply_training_to_player(player: Player, distribution: Dict[str, int]) -> Dict[str, Tuple[int, int]]:
    """
    Применяет изменения характеристик к игроку.
    Возвращает словарь изменений {attribute: (old_value, new_value)}
    """
    changes = {}
    age_modifier = player.get_age_training_modifier()
    
    for attr_name, points in distribution.items():
        if hasattr(player, attr_name):
            old_value = getattr(player, attr_name)
            
            # Для игроков 30+ лет тренировки могут быть отрицательными
            if age_modifier < 0.5 and random.random() < 0.3:  # 30% шанс деградации
                # Отрицательный эффект: теряем 1-2 очка
                points_change = -random.randint(1, 2)
            else:
                points_change = points
            
            new_value = max(1, min(99, old_value + points_change))
            setattr(player, attr_name, new_value)
            
            if old_value != new_value:
                changes[attr_name] = (old_value, new_value)
    
    # Сохраняем изменения
    player.save()
    return changes


def conduct_player_training(player: Player) -> Dict:
    """
    Проводит тренировку для одного игрока.
    Возвращает информацию о результатах тренировки.
    """
    # Проверяем, нужно ли активировать расцвет
    if player.should_start_bloom():
        player.start_bloom()
    
    # Вычисляем очки для тренировки
    total_points = calculate_training_points(player)
    
    # Распределяем очки между характеристиками
    distribution = distribute_training_points(player, total_points)
    
    # Применяем изменения
    changes = apply_training_to_player(player, distribution)
    
    return {
        'player_id': player.id,
        'player_name': player.full_name,
        'total_points': total_points,
        'is_in_bloom': player.is_in_bloom,
        'bloom_type': player.bloom_type if player.is_in_bloom else None,
        'age_modifier': player.get_age_training_modifier(),
        'changes': changes,
        'attributes_improved': len(changes)
    }


def conduct_team_training(club) -> List[Dict]:
    """
    Проводит тренировки для всех игроков клуба.
    Возвращает список результатов тренировок.
    """
    results = []
    
    # Получаем всех игроков клуба
    players = Player.objects.filter(club=club)
    
    for player in players:
        try:
            result = conduct_player_training(player)
            results.append(result)
        except Exception as e:
            # Логируем ошибку, но продолжаем тренировки других игроков
            results.append({
                'player_id': player.id,
                'player_name': player.full_name,
                'error': str(e)
            })
    
    return results


def conduct_all_teams_training() -> Dict:
    """
    Проводит тренировки для всех команд в системе.
    Возвращает общую статистику.
    """
    from clubs.models import Club
    
    stats = {
        'teams_trained': 0,
        'players_trained': 0,
        'total_improvements': 0,
        'players_in_bloom': 0,
        'errors': 0
    }
    
    clubs = Club.objects.all()
    
    for club in clubs:
        try:
            team_results = conduct_team_training(club)
            stats['teams_trained'] += 1
            
            for result in team_results:
                if 'error' in result:
                    stats['errors'] += 1
                else:
                    stats['players_trained'] += 1
                    stats['total_improvements'] += result.get('attributes_improved', 0)
                    if result.get('is_in_bloom', False):
                        stats['players_in_bloom'] += 1
                        
        except Exception as e:
            print(f"Ошибка при тренировке команды {club.name}: {e}")
            stats['errors'] += 1
    
    return stats