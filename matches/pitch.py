import random
from typing import Dict, List, Tuple, Optional
from players.models import Player

class Pitch:
    """
    Класс, представляющий футбольное поле как сетку.
    
    WIDTH = 100: ширина поля в клетках
    HEIGHT = 60: высота поля в клетках
    """
    WIDTH = 100
    HEIGHT = 60
    
    def __init__(self):
        # Позиции игроков в формате {(team_type, player_id): (x, y)}
        self.positions: Dict[Tuple[str, int], Tuple[int, int]] = {}
        # Позиция мяча (x, y)
        self.ball_position: Tuple[int, int] = (self.WIDTH // 2, self.HEIGHT // 2)
        # ID игрока, владеющего мячом
        self.ball_owner: Optional[Tuple[str, int]] = None
        
    def set_initial_positions(self, home_players: List[Player], away_players: List[Player]):
        """
        Расставляет игроков по начальным позициям в зависимости от их ролей.
        """
        # Очищаем текущие позиции
        self.positions.clear()
        
        # Расставляем домашнюю команду (атакует справа налево)
        self._set_team_positions(home_players, 'home')
        # Расставляем гостевую команду (атакует слева направо)
        self._set_team_positions(away_players, 'away')
        
    def _set_team_positions(self, players: List[Player], team_type: str):
        """
        Расставляет одну команду по позициям.
        """
        for player in players:
            x, y = self._get_initial_position(player.position, team_type)
            # Добавляем случайное смещение для разнообразия
            x += random.randint(-5, 5)
            y += random.randint(-3, 3)
            # Проверяем границы поля
            x = max(0, min(self.WIDTH - 1, x))
            y = max(0, min(self.HEIGHT - 1, y))
            self.positions[(team_type, player.id)] = (x, y)
    
    def _get_initial_position(self, position: str, team_type: str) -> Tuple[int, int]:
        """
        Определяет начальную позицию игрока в зависимости от его роли.
        """
        # Базовая x-координата зависит от команды
        if team_type == 'home':
            base_x = self.WIDTH * 3 // 4  # правая половина
        else:
            base_x = self.WIDTH // 4  # левая половина
            
        # Y-координата и смещение по X зависят от позиции игрока
        if 'Goalkeeper' in position:
            return (5 if team_type == 'away' else self.WIDTH - 5, self.HEIGHT // 2)
        elif 'Center Back' in position:
            return (base_x + (-10 if team_type == 'home' else 10), self.HEIGHT // 2)
        elif 'Right Back' in position:
            return (base_x + (-10 if team_type == 'home' else 10), self.HEIGHT * 3 // 4)
        elif 'Left Back' in position:
            return (base_x + (-10 if team_type == 'home' else 10), self.HEIGHT // 4)
        elif 'Defensive Midfielder' in position:
            return (base_x + (-5 if team_type == 'home' else 5), self.HEIGHT // 2)
        elif 'Central Midfielder' in position:
            return (base_x, self.HEIGHT // 2)
        elif 'Right Midfielder' in position:
            return (base_x, self.HEIGHT * 3 // 4)
        elif 'Left Midfielder' in position:
            return (base_x, self.HEIGHT // 4)
        elif 'Attacking Midfielder' in position:
            return (base_x + (5 if team_type == 'home' else -5), self.HEIGHT // 2)
        elif 'Center Forward' in position:
            return (base_x + (10 if team_type == 'home' else -10), self.HEIGHT // 2)
        else:
            return (base_x, self.HEIGHT // 2)

    def move_player(self, team_type: str, player_id: int, dx: int, dy: int) -> bool:
        """
        Перемещает игрока на dx, dy клеток.
        Возвращает True, если перемещение успешно.
        """
        if (team_type, player_id) not in self.positions:
            return False
            
        x, y = self.positions[(team_type, player_id)]
        new_x = max(0, min(self.WIDTH - 1, x + dx))
        new_y = max(0, min(self.HEIGHT - 1, y + dy))
        
        # Проверяем, не занята ли новая позиция
        for pos in self.positions.values():
            if pos == (new_x, new_y):
                return False
                
        self.positions[(team_type, player_id)] = (new_x, new_y)
        
        # Если у игрока был мяч, мяч движется с ним
        if self.ball_owner == (team_type, player_id):
            self.ball_position = (new_x, new_y)
            
        return True
        
    def move_towards(self, team_type: str, player_id: int, target_x: int, target_y: int, 
                    speed: int = 1) -> bool:
        """
        Перемещает игрока в направлении целевой точки.
        """
        if (team_type, player_id) not in self.positions:
            return False
            
        x, y = self.positions[(team_type, player_id)]
        dx = 0
        dy = 0
        
        if x < target_x:
            dx = min(speed, target_x - x)
        elif x > target_x:
            dx = max(-speed, target_x - x)
            
        if y < target_y:
            dy = min(speed, target_y - y)
        elif y > target_y:
            dy = max(-speed, target_y - y)
            
        return self.move_player(team_type, player_id, dx, dy)
        
    def get_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Вычисляет расстояние между двумя точками на поле.
        """
        x1, y1 = pos1
        x2, y2 = pos2
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        
    def get_nearest_players(self, x: int, y: int, team_type: str = None, 
                          max_distance: float = None) -> List[Tuple[Tuple[str, int], float]]:
        """
        Находит ближайших игроков к заданной точке.
        Можно отфильтровать по команде и максимальному расстоянию.
        Возвращает список кортежей ((team_type, player_id), distance).
        """
        players = []
        for (t, pid), pos in self.positions.items():
            if team_type and t != team_type:
                continue
                
            dist = self.get_distance((x, y), pos)
            if max_distance is None or dist <= max_distance:
                players.append(((t, pid), dist))
                
        return sorted(players, key=lambda x: x[1])
        
    def is_position_free(self, x: int, y: int, radius: int = 1) -> bool:
        """
        Проверяет, свободна ли позиция (с учетом радиуса).
        """
        for pos in self.positions.values():
            if self.get_distance((x, y), pos) <= radius:
                return False
        return True
        
    def get_team_average_position(self, team_type: str) -> Tuple[float, float]:
        """
        Вычисляет среднюю позицию команды на поле.
        """
        positions = [(x, y) for (t, _), (x, y) in self.positions.items() if t == team_type]
        if not positions:
            return (0, 0)
            
        avg_x = sum(x for x, _ in positions) / len(positions)
        avg_y = sum(y for _, y in positions) / len(positions)
        return (avg_x, avg_y)