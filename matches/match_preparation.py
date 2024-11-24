from typing import Dict, List, Tuple
from .models import Match
from clubs.models import Club
from players.models import Player

class PreMatchPreparation:
    """Класс для подготовки и анализа матча перед его началом"""
    
    # Веса для расчета силы игроков по позициям
    DEFENDER_WEIGHTS = {
        'marking': 0.3,
        'tackling': 0.3,
        'strength': 0.2,
        'positioning': 0.2
    }
    
    MIDFIELDER_WEIGHTS = {
        'passing': 0.3,
        'vision': 0.3,
        'stamina': 0.2,
        'work_rate': 0.2
    }
    
    FORWARD_WEIGHTS = {
        'finishing': 0.3,
        'dribbling': 0.3,
        'long_range': 0.2,
        'accuracy': 0.2
    }
    
    GOALKEEPER_WEIGHTS = {
        'reflexes': 0.25,
        'handling': 0.25,
        'positioning': 0.2,
        'aerial': 0.1,
        'command': 0.1,
        'shot_reading': 0.1
    }

    def __init__(self, match: Match):
        self.match = match
        self.home_team = match.home_team
        self.away_team = match.away_team
        
        # Проверяем и автоматически формируем составы если нужно
        self.home_lineup = self.match.home_lineup if self.match.home_lineup else self.auto_select_lineup(self.home_team)
        self.away_lineup = self.match.away_lineup if self.match.away_lineup else self.auto_select_lineup(self.away_team)
        
        # Сохраняем сформированные составы в матч
        if not self.match.home_lineup:
            self.match.home_lineup = self.home_lineup
        if not self.match.away_lineup:
            self.match.away_lineup = self.away_lineup
        self.match.save()
        
        # Результаты проверок и расчетов будут храниться здесь
        self.validation_results = {
            'home_valid': False,
            'away_valid': False,
            'errors': []
        }
        
        # Расчетные параметры команд
        self.team_strengths = {
            'home': 0,
            'away': 0
        }
        
        # Начальные параметры матча
        self.match_parameters = {
            'home': {
                'players_condition': {},  # Физическая готовность каждого игрока (100%)
                'team_attack': 0,        # Атакующий потенциал команды
                'team_defense': 0,       # Оборонительный потенциал команды
                'team_midfield': 0,      # Контроль средней линии
                'goalkeeper_strength': 0  # Сила вратаря
            },
            'away': {
                'players_condition': {},  # Физическая готовность каждого игрока (100%)
                'team_attack': 0,        # Атакующий потенциал команды
                'team_defense': 0,       # Оборонительный потенциал команды
                'team_midfield': 0,      # Контроль средней линии
                'goalkeeper_strength': 0  # Сила вратаря
            }
        }

    def auto_select_lineup(self, team: Club) -> dict:
        """
        Автоматически формирует состав команды в формате 4-4-2
        
        Args:
            team: Club - команда для которой формируется состав
            
        Returns:
            dict: словарь с расстановкой игроков
        """
        players = team.player_set.all()
        lineup = {}
        
        # Сначала выбираем вратаря
        goalkeeper = players.filter(position='Goalkeeper').first()
        if goalkeeper:
            lineup['0'] = goalkeeper.id
        
        # Выбираем защитников (4 позиции)
        defenders = players.filter(
            position__in=['Right Back', 'Left Back', 'Center Back']
        )[:4]
        for i, player in enumerate(defenders, 1):
            lineup[str(i)] = player.id
        
        # Выбираем полузащитников (4 позиции)
        midfielders = players.filter(
            position__icontains='Midfielder'
        )[:4]
        for i, player in enumerate(midfielders, 5):
            lineup[str(i)] = player.id
        
        # Выбираем нападающих (2 позиции)
        forwards = players.filter(
            position='Center Forward'
        )[:2]
        for i, player in enumerate(forwards, 9):
            lineup[str(i)] = player.id
            
        return lineup

    def validate_lineup(self, lineup: Dict, team: Club) -> bool:
        """
        Проверяет валидность состава команды
        
        Args:
            lineup: Dict - словарь с расстановкой игроков
            team: Club - команда для проверки
        
        Returns:
            bool: True если состав валиден, False если есть ошибки
        """
        errors = []
        
        # Проверка количества игроков
        if len(lineup) != 11:
            errors.append(f"Команда {team.name} должна иметь ровно 11 игроков в составе")
            return False
            
        position_counts = {
            'Goalkeeper': 0,
            'Defender': 0,
            'Midfielder': 0,
            'Forward': 0
        }
        
        # Проверяем каждую позицию в составе
        for pos, player_id in lineup.items():
            try:
                player = Player.objects.get(id=player_id)
                
                # Проверяем позицию игрока
                if player.position == 'Goalkeeper':
                    position_counts['Goalkeeper'] += 1
                elif 'Back' in player.position or player.position == 'Center Back':
                    position_counts['Defender'] += 1
                elif 'Midfielder' in player.position:
                    position_counts['Midfielder'] += 1
                elif 'Forward' in player.position:
                    position_counts['Forward'] += 1
                    
            except Player.DoesNotExist:
                errors.append(f"Игрок с ID {player_id} не найден")
                return False
        
        # Проверяем количество игроков на каждой позиции
        if position_counts['Goalkeeper'] != 1:
            errors.append(f"В составе команды {team.name} должен быть ровно 1 вратарь")
            return False
            
        if not (3 <= position_counts['Defender'] <= 5):
            errors.append(f"В составе команды {team.name} должно быть от 3 до 5 защитников")
            return False
            
        if not (2 <= position_counts['Midfielder'] <= 5):
            errors.append(f"В составе команды {team.name} должно быть от 2 до 5 полузащитников")
            return False
            
        if not (1 <= position_counts['Forward'] <= 4):
            errors.append(f"В составе команды {team.name} должно быть от 1 до 4 нападающих")
            return False
            
        # Добавляем ошибки в общий список
        if errors:
            self.validation_results['errors'].extend(errors)
            return False
            
        return True

    def calculate_player_strength(self, player: Player) -> float:
        """
        Рассчитывает силу игрока на его позиции
        
        Args:
            player: Player - игрок для расчета
            
        Returns:
            float: значение силы игрока (0-100)
        """
        if player.position == 'Goalkeeper':
            weights = self.GOALKEEPER_WEIGHTS
            attributes = {
                'reflexes': player.reflexes,
                'handling': player.handling,
                'positioning': player.positioning,
                'aerial': player.aerial,
                'command': player.command,
                'shot_reading': player.shot_reading
            }
        elif 'Back' in player.position or player.position == 'Center Back':
            weights = self.DEFENDER_WEIGHTS
            attributes = {
                'marking': player.marking,
                'tackling': player.tackling,
                'strength': player.strength,
                'positioning': player.positioning
            }
        elif 'Midfielder' in player.position:
            weights = self.MIDFIELDER_WEIGHTS
            attributes = {
                'passing': player.passing,
                'vision': player.vision,
                'stamina': player.stamina,
                'work_rate': player.work_rate
            }
        else:  # Forwards
            weights = self.FORWARD_WEIGHTS
            attributes = {
                'finishing': player.finishing,
                'dribbling': player.dribbling,
                'long_range': player.long_range,
                'accuracy': player.accuracy
            }
        
        # Рассчитываем взвешенную сумму характеристик
        strength = sum(weights[attr] * value for attr, value in attributes.items())
        return round(strength, 2)

    def calculate_team_strength(self, lineup: Dict, team: Club, is_home: bool = False) -> float:
        """
        Рассчитывает общую силу команды
        
        Args:
            lineup: Dict - словарь с расстановкой игроков
            team: Club - команда
            is_home: bool - играет ли команда дома
            
        Returns:
            float: общая сила команды (0-100)
        """
        total_strength = 0
        position_counts = {
            'Goalkeeper': 0,
            'Defender': 0,
            'Midfielder': 0,
            'Forward': 0
        }

        # Рассчитываем силу каждого игрока и суммируем
        for player_id in lineup.values():
            try:
                player = Player.objects.get(id=player_id)
                player_strength = self.calculate_player_strength(player)
                total_strength += player_strength

                # Подсчитываем количество игроков на каждой позиции
                if player.position == 'Goalkeeper':
                    position_counts['Goalkeeper'] += 1
                elif 'Back' in player.position or player.position == 'Center Back':
                    position_counts['Defender'] += 1
                elif 'Midfielder' in player.position:
                    position_counts['Midfielder'] += 1
                else:
                    position_counts['Forward'] += 1

            except Player.DoesNotExist:
                continue

        # Проверяем баланс состава
        if position_counts['Goalkeeper'] != 1:
            return 0  # Неверное количество вратарей
        if position_counts['Defender'] < 3 or position_counts['Defender'] > 5:
            return 0  # Слишком мало или много защитников
        if position_counts['Midfielder'] < 2 or position_counts['Midfielder'] > 5:
            return 0  # Слишком мало или много полузащитников
        if position_counts['Forward'] < 1 or position_counts['Forward'] > 4:
            return 0  # Слишком мало или много нападающих

        # Рассчитываем среднюю силу команды
        team_strength = total_strength / 11
        
        # Добавляем бонус за домашнее поле (+10%)
        if is_home:
            team_strength *= 1.1
            
        return round(team_strength, 2)

    def _calculate_initial_parameters(self, team_type: str):
        """
        Рассчитывает начальные параметры для команды
        
        Args:
            team_type: str - 'home' или 'away'
        """
        lineup = self.home_lineup if team_type == 'home' else self.away_lineup
        parameters = self.match_parameters[team_type]
        
        attack_sum = 0
        defense_sum = 0
        midfield_sum = 0
        attacker_count = 0
        defender_count = 0
        midfielder_count = 0
        
        # Проходим по всем игрокам в составе
        for position, player_id in lineup.items():
            player = Player.objects.get(id=player_id)
            
            # Устанавливаем начальную физическую готовность
            parameters['players_condition'][player_id] = 100
            
            if player.position == 'Goalkeeper':
                # Рассчитываем силу вратаря
                parameters['goalkeeper_strength'] = self.calculate_player_strength(player)
                
            elif 'Back' in player.position or player.position == 'Center Back':
                # Защитники
                defense_sum += (
                    player.marking * 0.3 +
                    player.tackling * 0.3 +
                    player.strength * 0.2 +
                    player.positioning * 0.2
                )
                defender_count += 1
                
            elif 'Midfielder' in player.position:
                # Полузащитники
                midfield_sum += (
                    player.passing * 0.3 +
                    player.vision * 0.3 +
                    player.work_rate * 0.2 +
                    player.stamina * 0.2
                )
                midfielder_count += 1
                
                # Атакующие полузащитники вносят вклад в атаку
                if 'Attacking' in player.position:
                    attack_sum += (
                        player.finishing * 0.2 +
                        player.long_range * 0.2 +
                        player.accuracy * 0.1
                    )
                    attacker_count += 0.5  # Считаем как пол-нападающего
                    
            else:
                # Нападающие
                attack_sum += (
                    player.finishing * 0.3 +
                    player.dribbling * 0.3 +
                    player.long_range * 0.2 +
                    player.accuracy * 0.2
                )
                attacker_count += 1
        
        # Рассчитываем средние значения
        parameters['team_attack'] = round(attack_sum / max(attacker_count, 1), 2)
        parameters['team_defense'] = round(defense_sum / defender_count, 2)
        parameters['team_midfield'] = round(midfield_sum / midfielder_count, 2)
        
        # Применяем домашний бонус
        if team_type == 'home':
            parameters['team_attack'] *= 1.1
            parameters['team_defense'] *= 1.1
            parameters['team_midfield'] *= 1.1

    def prepare_match(self) -> bool:
        """
        Основной метод подготовки матча
        
        Returns:
            bool: True если подготовка успешна, False если есть ошибки
        """
        # Проверяем составы
        self.validation_results['home_valid'] = self.validate_lineup(self.home_lineup, self.home_team)
        self.validation_results['away_valid'] = self.validate_lineup(self.away_lineup, self.away_team)
        
        # Если есть ошибки в составах, дальнейшая подготовка невозможна
        if not (self.validation_results['home_valid'] and self.validation_results['away_valid']):
            return False
            
        # Рассчитываем силу команд
        self.team_strengths['home'] = self.calculate_team_strength(
            self.home_lineup, 
            self.home_team, 
            is_home=True
        )
        self.team_strengths['away'] = self.calculate_team_strength(
            self.away_lineup, 
            self.away_team, 
            is_home=False
        )
        
        # Проверяем валидность рассчитанных сил
        if self.team_strengths['home'] == 0 or self.team_strengths['away'] == 0:
            self.validation_results['errors'].append("Ошибка в расчете сил команд - неверный баланс состава")
            return False
        
        # Рассчитываем начальные параметры матча
        self._calculate_initial_parameters('home')
        self._calculate_initial_parameters('away')
        
        return True

    def get_validation_errors(self) -> List[str]:
        """Возвращает список ошибок валидации"""
        return self.validation_results['errors']