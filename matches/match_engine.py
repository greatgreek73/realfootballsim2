from typing import Dict, List, Tuple
from .models import Match, MatchEvent
from .match_preparation import PreMatchPreparation
import random
from django.utils import timezone

class MatchEngine:
    """Основной движок симуляции матча"""
    
    # Временные периоды матча
    PERIODS = [
        (0, 15),    # Начало матча
        (15, 30),   # Первый тайм
        (30, 45),   # Конец первого тайма
        (45, 60),   # Начало второго тайма
        (60, 75),   # Второй тайм
        (75, 90),   # Концовка матча
    ]
    
    # Модификаторы событий для разных периодов
    PERIOD_MODIFIERS = {
        0: {  # Начало матча
            'attack_chance': 0.8,    # Осторожное начало
            'goal_chance': 0.7,      # Меньше голов
            'fatigue_rate': 0.5      # Медленное утомление
        },
        1: {  # Первый тайм
            'attack_chance': 1.0,    # Нормальная активность
            'goal_chance': 1.0,      # Обычная реализация
            'fatigue_rate': 1.0      # Обычное утомление
        },
        2: {  # Конец первого тайма
            'attack_chance': 1.1,    # Повышенная активность
            'goal_chance': 1.2,      # Больше голов
            'fatigue_rate': 1.2      # Быстрое утомление
        },
        3: {  # Начало второго тайма
            'attack_chance': 0.9,    # Разминка после перерыва
            'goal_chance': 0.9,      # Меньше голов
            'fatigue_rate': 0.8      # Восстановление после перерыва
        },
        4: {  # Второй тайм
            'attack_chance': 1.0,    # Нормальная активность
            'goal_chance': 1.1,      # Чуть больше голов
            'fatigue_rate': 1.1      # Повышенное утомление
        },
        5: {  # Концовка матча
            'attack_chance': 1.3,    # Высокая активность
            'goal_chance': 1.4,      # Много голов
            'fatigue_rate': 1.5      # Сильное утомление
        }
    }

    def __init__(self, match: Match):
        self.match = match
        self.preparation = PreMatchPreparation(match)
        
        if not self.preparation.prepare_match():
            raise ValueError("Ошибка подготовки матча")
            
        self.match_stats = {
            'home': {
                'possession': 50,     # Владение мячом
                'shots': 0,           # Удары
                'shots_on_target': 0, # Удары в створ
                'corners': 0,         # Угловые
                'fouls': 0,          # Фолы
                'attacks': 0,         # Атаки
                'dangerous_attacks': 0 # Опасные атаки
            },
            'away': {
                'possession': 50,
                'shots': 0,
                'shots_on_target': 0,
                'corners': 0,
                'fouls': 0,
                'attacks': 0,
                'dangerous_attacks': 0
            }
        }
        
        # Копируем начальные параметры из подготовки
        self.match_parameters = self.preparation.match_parameters
        
    def get_period_index(self, minute: int) -> int:
        """Определяет индекс текущего периода матча"""
        for i, (start, end) in enumerate(self.PERIODS):
            if start <= minute < end:
                return i
        return 5  # Концовка матча
        
    def update_player_condition(self, team_type: str, player_id: int, minute: int):
        """Обновляет физическую готовность игрока"""
        player_condition = self.match_parameters[team_type]['players_condition'][player_id]
        period_index = self.get_period_index(minute)
        fatigue_rate = self.PERIOD_MODIFIERS[period_index]['fatigue_rate']
        
        # Получаем выносливость игрока
        player = self.match.home_team.player_set.get(id=player_id) if team_type == 'home' \
            else self.match.away_team.player_set.get(id=player_id)
        
        # Чем выше выносливость, тем медленнее падает готовность
        stamina_factor = player.stamina / 100
        
        # Обновляем готовность
        new_condition = player_condition - (1 - stamina_factor) * fatigue_rate
        self.match_parameters[team_type]['players_condition'][player_id] = max(0, new_condition)
        
    def calculate_attack_success(self, attacking_team: str, minute: int) -> float:
        """
        Рассчитывает вероятность успеха атаки
        
        Args:
            attacking_team: str - 'home' или 'away'
            minute: int - текущая минута матча
            
        Returns:
            float: вероятность успеха атаки (0-1)
        """
        defending_team = 'away' if attacking_team == 'home' else 'home'
        period_index = self.get_period_index(minute)
        
        # Базовые параметры
        attack_power = self.match_parameters[attacking_team]['team_attack']
        defense_power = self.match_parameters[defending_team]['team_defense']
        midfield_power = self.match_parameters[attacking_team]['team_midfield']
        
        # Рассчитываем среднюю готовность команд
        attack_condition = sum(self.match_parameters[attacking_team]['players_condition'].values()) / 11
        defense_condition = sum(self.match_parameters[defending_team]['players_condition'].values()) / 11
        
        # Применяем готовность к силе команд
        attack_power *= (attack_condition / 100)
        defense_power *= (defense_condition / 100)
        
        # Рассчитываем базовую вероятность
        base_chance = (attack_power + midfield_power/2) / (defense_power + 50)
        
        # Применяем модификатор периода
        period_modifier = self.PERIOD_MODIFIERS[period_index]['attack_chance']
        
        return min(0.9, base_chance * period_modifier)  # Максимум 90% шанс

    def simulate_minute(self, minute: int):
        """
        Симулирует одну минуту матча
        
        Args:
            minute: int - текущая минута
        """
        period_index = self.get_period_index(minute)
        modifiers = self.PERIOD_MODIFIERS[period_index]
        
        # Обновляем готовность игроков
        for team_type in ['home', 'away']:
            for player_id in self.match_parameters[team_type]['players_condition'].keys():
                self.update_player_condition(team_type, player_id, minute)
        
        # Определяем владение мячом на основе силы полузащиты
        home_mid = self.match_parameters['home']['team_midfield']
        away_mid = self.match_parameters['away']['team_midfield']
        total_mid = home_mid + away_mid
        
        self.match_stats['home']['possession'] = round((home_mid / total_mid) * 100)
        self.match_stats['away']['possession'] = 100 - self.match_stats['home']['possession']
        
        # Определяем атакующую команду
        if random.random() < (self.match_stats['home']['possession'] / 100):
            attacking_team = 'home'
            defending_team = 'away'
        else:
            attacking_team = 'away'
            defending_team = 'home'
        
        # Пытаемся создать атаку
        attack_chance = self.calculate_attack_success(attacking_team, minute)
        if random.random() < attack_chance * modifiers['attack_chance']:
            self.match_stats[attacking_team]['attacks'] += 1
            
            # Пытаемся создать опасный момент
            shot_chance = attack_chance * modifiers['goal_chance']
            if random.random() < shot_chance:
                self.match_stats[attacking_team]['dangerous_attacks'] += 1
                self.match_stats[attacking_team]['shots'] += 1
                
                # Определяем, попал ли удар в створ
                on_target = random.random() < 0.6  # 60% ударов в створ
                if on_target:
                    self.match_stats[attacking_team]['shots_on_target'] += 1
                    
                    # Пытаемся забить гол
                    attacking_power = self.match_parameters[attacking_team]['team_attack']
                    goalkeeper_power = self.match_parameters[defending_team]['goalkeeper_strength']
                    
                    # Учитываем усталость
                    team_condition = sum(self.match_parameters[attacking_team]['players_condition'].values()) / 11
                    attacking_power *= (team_condition / 100)
                    
                    # Шанс гола зависит от атаки и силы вратаря
                    goal_chance = (attacking_power / (goalkeeper_power + attacking_power)) * modifiers['goal_chance']
                    
                    if random.random() < goal_chance:
                        # Гол!
                        if attacking_team == 'home':
                            self.match.home_score += 1
                        else:
                            self.match.away_score += 1
                            
                        # Выбираем автора гола
                        team = self.match.home_team if attacking_team == 'home' else self.match.away_team
                        scorer = None
                        
                        # Пытаемся выбрать нападающего или атакующего полузащитника
                        attackers = team.player_set.filter(
                            models.Q(position='Center Forward') |
                            models.Q(position='Attacking Midfielder')
                        )
                        if attackers.exists():
                            scorer = random.choice(attackers)
                        else:
                            # Если нет, выбираем любого полевого игрока
                            scorer = random.choice(
                                team.player_set.exclude(position='Goalkeeper')
                            )
                            
                        # Создаем событие гола
                        MatchEvent.objects.create(
                            match=self.match,
                            minute=minute,
                            event_type='goal',
                            player=scorer,
                            description=f"Goal scored by {scorer.full_name}"
                        )
                        
                        # Сохраняем текущий счет
                        self.match.save()
                        
                else:
                    # Удар мимо, шанс углового 40%
                    if random.random() < 0.4:
                        self.match_stats[attacking_team]['corners'] += 1
        
        # Шанс фола (зависит от усталости и периода)
        foul_chance = 0.1 * modifiers['fatigue_rate']  # Базовый шанс 10%
        if random.random() < foul_chance:
            self.match_stats[defending_team]['fouls'] += 1
        
    def simulate_match(self):
        """Запускает полную симуляцию матча"""
        # Устанавливаем начальный статус
        self.match.status = 'in_progress'
        self.match.save()
        
        # Симулируем каждую минуту
        for minute in range(90):
            self.simulate_minute(minute)
            
        # Завершаем матч
        self.match.status = 'finished'
        self.match.save()