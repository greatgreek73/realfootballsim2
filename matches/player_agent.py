import random

class PlayerAgent:
    def __init__(self, player_model):
        # Базовая информация
        self.player_model = player_model
        self.full_name = player_model.full_name
        self.position = player_model.position
        
        # Базовые характеристики
        self.condition = 100  # Физическое состояние
        self.morale = 100    # Моральное состояние
        
    def decide_action(self, match_state):
        """Принятие решения о следующем действии"""
        if self.position in ['Center Forward', 'Attacking Midfielder']:
            return 'attack' if random.random() < 0.7 else 'position'
        elif self.position == 'Midfielder':
            return 'attack' if random.random() < 0.5 else 'position'
        else:
            return 'position'

    def perform_action(self, action, match_state):
        """Выполнение действия"""
        # Простая реализация - возвращаем True/False для успеха/неудачи
        if action == 'attack':
            return random.random() < 0.4
        elif action == 'position':
            return True
        return False