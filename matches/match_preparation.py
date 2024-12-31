from typing import Dict, List
from .models import Match
from clubs.models import Club
from players.models import Player
import logging

logger = logging.getLogger(__name__)

class PreMatchPreparation:
    """Класс для подготовки и анализа матча перед его началом"""

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

        # 1) Берём состав из match.home_lineup / match.away_lineup
        #    Если там пусто — пытаемся взять из club.lineup
        #    Если и там пусто — авто-выбор (4-4-2)
        self.home_lineup = match.home_lineup or self.get_lineup_from_club(self.home_team) or self.auto_select_lineup(self.home_team)
        self.away_lineup = match.away_lineup or self.get_lineup_from_club(self.away_team) or self.auto_select_lineup(self.away_team)

        # 2) Сохраняем обратно в match (чтобы зафиксировать)
        if not match.home_lineup:
            match.home_lineup = self.home_lineup
        if not match.away_lineup:
            match.away_lineup = self.away_lineup
        match.save()

        # Итог: теперь match.home_lineup/match.away_lineup заполнены

        self.validation_results = {
            'home_valid': False,
            'away_valid': False,
            'errors': []
        }

        self.team_strengths = {
            'home': 0,
            'away': 0
        }

        self.match_parameters = {
            'home': {
                'players_condition': {},
                'team_attack': 0,
                'team_defense': 0,
                'team_midfield': 0,
                'goalkeeper_strength': 0
            },
            'away': {
                'players_condition': {},
                'team_attack': 0,
                'team_defense': 0,
                'team_midfield': 0,
                'goalkeeper_strength': 0
            }
        }

    def get_lineup_from_club(self, club: Club) -> dict:
        """
        Берём lineup из club.lineup (если он есть).
        club.lineup — это dict вида: {'lineup': {...}, 'tactic': '???'}
        
        Возвращает именно 'lineup' или None, если что-то не так.
        """
        if not club.lineup:
            return None
        if 'lineup' not in club.lineup:
            return None

        # Пример: club.lineup = {"lineup": {"0": 123, "1": 456, ...}, "tactic": "balanced"}
        # Тут lineup = {"0": 123, "1": 456, ...}
        lineup_dict = club.lineup.get('lineup', {})
        if not isinstance(lineup_dict, dict):
            return None

        if len(lineup_dict) < 11:
            # Либо считаем, что lineup неполный => None
            return None

        logger.info(f"[PreMatch] Using club.lineup for {club.name}: {lineup_dict}")
        return lineup_dict

    def auto_select_lineup(self, team: Club) -> dict:
        """
        Автоматически формирует состав команды (4-4-2).
        """
        players = team.player_set.all()
        lineup = {}

        # Сначала вратарь
        goalkeeper = players.filter(position='Goalkeeper').first()
        if goalkeeper:
            lineup['0'] = goalkeeper.id

        # Защитники (4)
        defenders = players.filter(
            position__in=['Right Back', 'Left Back', 'Center Back']
        )[:4]
        idx = 1
        for player in defenders:
            lineup[str(idx)] = player.id
            idx += 1

        # Полузащитники (4)
        midfielders = players.filter(
            position__icontains='Midfielder'
        )[:4]
        for m in midfielders:
            lineup[str(idx)] = m.id
            idx += 1

        # Нападающие (2)
        forwards = players.filter(position='Center Forward')[:2]
        for f in forwards:
            lineup[str(idx)] = f.id
            idx += 1

        logger.info(f"[PreMatch] Auto lineup (4-4-2) for {team.name}: {lineup}")
        return lineup

    def validate_lineup(self, lineup: Dict, team: Club) -> bool:
        """
        Проверяет валидность состава (11 человек, 1 GK, и т.д.)
        """
        errors = []

        # 11 игроков
        if len(lineup) != 11:
            errors.append(f"Team {team.name} must have exactly 11 players in lineup.")
            self.validation_results['errors'].extend(errors)
            return False

        position_counts = {
            'Goalkeeper': 0,
            'Defender': 0,
            'Midfielder': 0,
            'Forward': 0
        }

        for pos_key, player_id in lineup.items():
            try:
                player = Player.objects.get(id=player_id)
                if player.position == 'Goalkeeper':
                    position_counts['Goalkeeper'] += 1
                elif 'Back' in player.position:
                    position_counts['Defender'] += 1
                elif 'Midfielder' in player.position:
                    position_counts['Midfielder'] += 1
                else:
                    # Считаем всё остальное форвардом (Center Forward etc.)
                    position_counts['Forward'] += 1
            except Player.DoesNotExist:
                errors.append(f"Player with ID {player_id} not found.")
                self.validation_results['errors'].extend(errors)
                return False

        if position_counts['Goalkeeper'] != 1:
            errors.append(f"Team {team.name} must have exactly 1 goalkeeper.")
        if position_counts['Defender'] < 3 or position_counts['Defender'] > 5:
            errors.append(f"Team {team.name} must have between 3 and 5 defenders.")
        if position_counts['Midfielder'] < 2 or position_counts['Midfielder'] > 5:
            errors.append(f"Team {team.name} must have between 2 and 5 midfielders.")
        if position_counts['Forward'] < 1 or position_counts['Forward'] > 4:
            errors.append(f"Team {team.name} must have between 1 and 4 forwards.")

        if errors:
            self.validation_results['errors'].extend(errors)
            return False

        return True

    def calculate_player_strength(self, player: Player) -> float:
        """
        Рассчитываем силу игрока на его позиции (простейшая схема).
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
        elif 'Back' in player.position:
            # Защитник
            weights = self.DEFENDER_WEIGHTS
            attributes = {
                'marking': player.marking,
                'tackling': player.tackling,
                'strength': player.strength,
                'positioning': player.positioning
            }
        elif 'Midfielder' in player.position:
            # Полузащитник
            weights = self.MIDFIELDER_WEIGHTS
            attributes = {
                'passing': player.passing,
                'vision': player.vision,
                'stamina': player.stamina,
                'work_rate': player.work_rate
            }
        else:
            # Форвард
            weights = self.FORWARD_WEIGHTS
            attributes = {
                'finishing': player.finishing,
                'dribbling': player.dribbling,
                'long_range': player.long_range,
                'accuracy': player.accuracy
            }

        strength = sum(weights[attr] * attributes[attr] for attr in weights)
        return round(strength, 2)

    def calculate_team_strength(self, lineup: Dict, team: Club, is_home: bool=False) -> float:
        total_strength = 0
        for player_id in lineup.values():
            try:
                player = Player.objects.get(id=player_id)
                total_strength += self.calculate_player_strength(player)
            except Player.DoesNotExist:
                pass

        # Среднее
        avg_strength = total_strength / 11 if len(lineup) == 11 else 0
        if is_home:
            avg_strength *= 1.1
        return round(avg_strength, 2)

    def _calculate_initial_parameters(self, team_type: str):
        """
        Заполняем match_parameters[...] какими-то начальными значениями 
        (атака, защита, и т.д.).
        """
        lineup = self.home_lineup if team_type == 'home' else self.away_lineup
        parameters = self.match_parameters[team_type]

        # Примерная логика
        for _, player_id in lineup.items():
            parameters['players_condition'][player_id] = 100

        # Здесь можно делать любые расчёты, как у вас в коде
        parameters['team_attack'] = self.calculate_team_strength(lineup, None, is_home=(team_type=='home'))
        parameters['team_defense'] = parameters['team_attack'] * 0.8
        parameters['team_midfield'] = parameters['team_attack'] * 0.9
        parameters['goalkeeper_strength'] = parameters['team_attack'] * 0.7

    def prepare_match(self) -> bool:
        # 1) Проверяем составы
        self.validation_results['home_valid'] = self.validate_lineup(self.home_lineup, self.home_team)
        self.validation_results['away_valid'] = self.validate_lineup(self.away_lineup, self.away_team)

        if not (self.validation_results['home_valid'] and self.validation_results['away_valid']):
            return False

        # 2) Рассчитываем силы
        self.team_strengths['home'] = self.calculate_team_strength(self.home_lineup, self.home_team, True)
        self.team_strengths['away'] = self.calculate_team_strength(self.away_lineup, self.away_team, False)

        # 3) Начальные параметры
        self._calculate_initial_parameters('home')
        self._calculate_initial_parameters('away')

        # Если надо, можно логировать
        logger.info(f"[PreMatch] {self.home_team.name} strength={self.team_strengths['home']} lineup={self.home_lineup}")
        logger.info(f"[PreMatch] {self.away_team.name} strength={self.team_strengths['away']} lineup={self.away_lineup}")

        return True

    def get_validation_errors(self) -> List[str]:
        return self.validation_results['errors']
