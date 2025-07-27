# matches/narrative_system.py

import random
from datetime import date, timedelta
from django.db.models import Q
from django.conf import settings
from .models import PlayerRivalry, TeamChemistry, CharacterEvolution, NarrativeEvent
from players.models import Player


class RivalryManager:
    """
    Управляет соперничеством между игроками
    """
    
    # Интенсивность соперничества и её влияние
    INTENSITY_EFFECTS = {
        'mild': {'aggression': 0.1, 'performance': 0.05},
        'moderate': {'aggression': 0.2, 'performance': 0.1},
        'strong': {'aggression': 0.3, 'performance': 0.15},
        'intense': {'aggression': 0.5, 'performance': 0.25},
    }
    
    @classmethod
    def create_rivalry(cls, player1, player2, rivalry_type='competitive', intensity='mild'):
        """
        Создает соперничество между двумя игроками
        """
        if player1.id == player2.id:
            return None
            
        # Проверяем, существует ли уже соперничество
        existing = PlayerRivalry.objects.filter(
            Q(player1=player1, player2=player2) | 
            Q(player1=player2, player2=player1)
        ).first()
        
        if existing:
            return existing
            
        # Создаем новое соперничество
        effects = cls.INTENSITY_EFFECTS[intensity]
        rivalry = PlayerRivalry.objects.create(
            player1=player1,
            player2=player2,
            rivalry_type=rivalry_type,
            intensity=intensity,
            aggression_modifier=effects['aggression'],
            performance_modifier=effects['performance']
        )
        
        return rivalry
    
    @classmethod
    def get_rivalry_between(cls, player1, player2):
        """
        Возвращает соперничество между двумя игроками (если существует)
        """
        return PlayerRivalry.objects.filter(
            Q(player1=player1, player2=player2) | 
            Q(player1=player2, player2=player1)
        ).first()
    
    @classmethod
    def get_player_rivalries(cls, player):
        """
        Возвращает все соперничества игрока
        """
        return PlayerRivalry.objects.filter(
            Q(player1=player) | Q(player2=player)
        )
    
    @classmethod
    def update_rivalry_interaction(cls, player1, player2, interaction_type='normal'):
        """
        Обновляет взаимодействие между соперниками
        """
        rivalry = cls.get_rivalry_between(player1, player2)
        if not rivalry:
            return None
            
        rivalry.last_interaction = date.today()
        rivalry.interaction_count += 1
        
        # Возможность усиления соперничества при конфликтных взаимодействиях
        if interaction_type == 'aggressive' and rivalry.intensity == 'mild':
            rivalry.intensity = 'moderate'
            effects = cls.INTENSITY_EFFECTS['moderate']
            rivalry.aggression_modifier = effects['aggression']
            rivalry.performance_modifier = effects['performance']
        
        rivalry.save()
        return rivalry
    
    @classmethod
    def generate_random_rivalries(cls, club_players, count=2):
        """
        Генерирует случайные соперничества между игроками клуба
        """
        if len(club_players) < 2:
            return []
            
        rivalries = []
        attempts = 0
        max_attempts = count * 3
        
        while len(rivalries) < count and attempts < max_attempts:
            player1, player2 = random.sample(list(club_players), 2)
            
            # Проверяем, что соперничества еще нет
            if not cls.get_rivalry_between(player1, player2):
                rivalry_type = random.choice(['competitive', 'personal', 'positional'])
                intensity = random.choices(
                    ['mild', 'moderate', 'strong'],
                    weights=[60, 30, 10]
                )[0]
                
                rivalry = cls.create_rivalry(player1, player2, rivalry_type, intensity)
                if rivalry:
                    rivalries.append(rivalry)
            
            attempts += 1
        
        return rivalries


class ChemistryCalculator:
    """
    Вычисляет и управляет химией между игроками команды
    """
    
    # Типы химии и их эффекты
    CHEMISTRY_EFFECTS = {
        'friendship': {'passing': 0.1, 'teamwork': 0.15},
        'mentor_mentee': {'passing': 0.05, 'teamwork': 0.25},
        'partnership': {'passing': 0.2, 'teamwork': 0.1},
        'leadership': {'passing': 0.05, 'teamwork': 0.3},
    }
    
    @classmethod
    def create_chemistry(cls, player1, player2, chemistry_type='friendship', strength=0.5):
        """
        Создает химию между двумя игроками
        """
        if player1.id == player2.id:
            return None
            
        # Проверяем, существует ли уже химия
        existing = TeamChemistry.objects.filter(
            Q(player1=player1, player2=player2) | 
            Q(player1=player2, player2=player1)
        ).first()
        
        if existing:
            return existing
            
        # Создаем новую химию
        effects = cls.CHEMISTRY_EFFECTS[chemistry_type]
        chemistry = TeamChemistry.objects.create(
            player1=player1,
            player2=player2,
            chemistry_type=chemistry_type,
            strength=strength,
            passing_bonus=effects['passing'] * strength,
            teamwork_bonus=effects['teamwork'] * strength
        )
        
        return chemistry
    
    @classmethod
    def get_chemistry_between(cls, player1, player2):
        """
        Возвращает химию между двумя игроками (если существует)
        """
        return TeamChemistry.objects.filter(
            Q(player1=player1, player2=player2) | 
            Q(player1=player2, player2=player1)
        ).first()
    
    @classmethod
    def get_player_chemistry(cls, player):
        """
        Возвращает всю химию игрока с другими
        """
        return TeamChemistry.objects.filter(
            Q(player1=player) | Q(player2=player)
        )
    
    @classmethod
    def calculate_team_chemistry_score(cls, players):
        """
        Вычисляет общий счет химии команды
        """
        total_chemistry = 0
        pair_count = 0
        
        for i, player1 in enumerate(players):
            for player2 in players[i+1:]:
                chemistry = cls.get_chemistry_between(player1, player2)
                if chemistry:
                    total_chemistry += chemistry.strength
                pair_count += 1
        
        return total_chemistry / pair_count if pair_count > 0 else 0
    
    @classmethod
    def update_chemistry_interaction(cls, player1, player2, interaction_type='positive'):
        """
        Обновляет взаимодействие между игроками с хорошей химией
        """
        chemistry = cls.get_chemistry_between(player1, player2)
        if not chemistry:
            return None
            
        if interaction_type == 'positive':
            chemistry.last_positive_interaction = date.today()
            chemistry.positive_interactions += 1
            
            # Возможность улучшения химии
            if chemistry.strength < 1.0:
                chemistry.strength = min(1.0, chemistry.strength + 0.01)
                
                # Обновляем бонусы
                effects = cls.CHEMISTRY_EFFECTS[chemistry.chemistry_type]
                chemistry.passing_bonus = effects['passing'] * chemistry.strength
                chemistry.teamwork_bonus = effects['teamwork'] * chemistry.strength
        
        chemistry.save()
        return chemistry
    
    @classmethod
    def generate_random_chemistry(cls, club_players, count=3):
        """
        Генерирует случайную химию между игроками клуба
        """
        if len(club_players) < 2:
            return []
            
        chemistry_bonds = []
        attempts = 0
        max_attempts = count * 3
        
        while len(chemistry_bonds) < count and attempts < max_attempts:
            player1, player2 = random.sample(list(club_players), 2)
            
            # Проверяем, что химии еще нет
            if not cls.get_chemistry_between(player1, player2):
                chemistry_type = random.choice(['friendship', 'mentor_mentee', 'partnership'])
                strength = random.uniform(0.3, 0.8)
                
                chemistry = cls.create_chemistry(player1, player2, chemistry_type, strength)
                if chemistry:
                    chemistry_bonds.append(chemistry)
            
            attempts += 1
        
        return chemistry_bonds


class EvolutionEngine:
    """
    Управляет эволюцией характера игроков
    """
    
    # Триггеры эволюции и их влияние на характеристики
    EVOLUTION_RULES = {
        'goal_scored': {
            'confidence': (1, 3),
            'ambition': (0, 2),
        },
        'match_won': {
            'confidence': (0, 2),
            'teamwork': (0, 1),
        },
        'match_lost': {
            'confidence': (-2, 0),
            'patience': (-1, 1),
        },
        'rivalry_interaction': {
            'aggression': (1, 3),
            'confidence': (-1, 2),
        },
        'team_chemistry': {
            'teamwork': (1, 2),
            'charisma': (0, 1),
        },
        'injury': {
            'confidence': (-3, -1),
            'endurance': (-1, 0),
        },
        'captain_appointment': {
            'leadership': (2, 5),
            'confidence': (1, 3),
            'charisma': (1, 2),
        },
    }
    
    @classmethod
    def evolve_personality(cls, player, trigger_event, match=None, related_player=None):
        """
        Эволюционирует личность игрока на основе события
        """
        if not hasattr(player, 'personality_traits') or not player.personality_traits:
            return None
            
        if trigger_event not in cls.EVOLUTION_RULES:
            return None
            
        # Получаем правила эволюции для события
        rules = cls.EVOLUTION_RULES[trigger_event]
        evolutions = []
        
        for trait, (min_change, max_change) in rules.items():
            if trait in player.personality_traits:
                # Вычисляем изменение
                change = random.randint(min_change, max_change)
                if change == 0:
                    continue
                    
                old_value = player.personality_traits[trait]
                new_value = max(0, min(100, old_value + change))
                
                if new_value != old_value:
                    # Записываем эволюцию
                    evolution = CharacterEvolution.objects.create(
                        player=player,
                        trigger_event=trigger_event,
                        trait_changed=trait,
                        old_value=old_value,
                        new_value=new_value,
                        change_amount=change,
                        match=match,
                        related_player=related_player
                    )
                    evolutions.append(evolution)
                    
                    # Обновляем черту у игрока
                    player.personality_traits[trait] = new_value
        
        if evolutions:
            player.save()
            
        return evolutions
    
    @classmethod
    def get_player_evolution_history(cls, player, limit=10):
        """
        Возвращает историю эволюции игрока
        """
        return CharacterEvolution.objects.filter(player=player)[:limit]
    
    @classmethod
    def calculate_personality_stability(cls, player):
        """
        Вычисляет стабильность личности игрока (как часто она меняется)
        """
        recent_evolutions = CharacterEvolution.objects.filter(
            player=player,
            timestamp__gte=date.today() - timedelta(days=30)
        ).count()
        
        # Чем больше изменений, тем меньше стабильность
        stability = max(0, 1.0 - (recent_evolutions * 0.1))
        return stability


class NarrativeGenerator:
    """
    Генерирует нарративные события и истории
    """
    
    # Шаблоны для генерации историй
    STORY_TEMPLATES = {
        'rivalry_clash': {
            'titles': [
                "Clash of Titans: {player1} vs {player2}",
                "Old Rivals Meet Again: {player1} and {player2}",
                "Fire and Ice: {player1} faces {player2}",
            ],
            'descriptions': [
                "The tension was palpable as {player1} and {player2} faced off once again. Their rivalry, spanning {duration}, reached new heights in minute {minute}.",
                "History repeated itself as {player1} and {player2} clashed in a moment that reminded everyone why their rivalry is legendary.",
            ]
        },
        'chemistry_moment': {
            'titles': [
                "Perfect Understanding: {player1} and {player2}",
                "Telepathic Connection: {player1} finds {player2}",
                "Chemistry in Action: {player1} & {player2}",
            ],
            'descriptions': [
                "In minute {minute}, {player1} and {player2} showed why they are perfectly in sync, demonstrating the kind of understanding that only comes from true chemistry.",
                "The connection between {player1} and {player2} was evident as they combined brilliantly in minute {minute}.",
            ]
        },
        'character_growth': {
            'titles': [
                "Coming of Age: {player1}",
                "New {player1}: Character Development",
                "Evolution: {player1}'s Journey",
            ],
            'descriptions': [
                "In minute {minute}, we witnessed a defining moment for {player1}. This experience will shape their character for matches to come.",
                "{player1} showed remarkable growth in minute {minute}, proving that they are evolving not just as a player, but as a person.",
            ]
        },
    }
    
    @classmethod
    def create_narrative_event(cls, event_type, primary_player, match, minute, 
                             secondary_player=None, importance='minor', **context):
        """
        Создает нарративное событие
        """
        if event_type not in cls.STORY_TEMPLATES:
            return None
            
        template = cls.STORY_TEMPLATES[event_type]
        
        # Выбираем случайный заголовок и описание
        title_template = random.choice(template['titles'])
        description_template = random.choice(template['descriptions'])
        
        # Форматируем строки
        format_data = {
            'player1': primary_player.full_name,
            'player2': secondary_player.full_name if secondary_player else 'teammate',
            'minute': minute,
            **context
        }
        
        title = title_template.format(**format_data)
        description = description_template.format(**format_data)
        
        # Создаем событие
        narrative_event = NarrativeEvent.objects.create(
            event_type=event_type,
            importance=importance,
            primary_player=primary_player,
            secondary_player=secondary_player,
            match=match,
            minute=minute,
            title=title,
            description=description
        )
        
        return narrative_event
    
    @classmethod
    def detect_narrative_opportunities(cls, match, minute, event_data):
        """
        Обнаруживает возможности для создания нарративных событий
        """
        events = []
        
        # Получаем игроков, участвующих в событии
        primary_player = event_data.get('player')
        secondary_player = event_data.get('related_player')
        
        if not primary_player:
            return events
            
        # Проверяем на соперничество
        if secondary_player:
            rivalry = RivalryManager.get_rivalry_between(primary_player, secondary_player)
            if rivalry and rivalry.intensity in ['strong', 'intense']:
                event = cls.create_narrative_event(
                    'rivalry_clash',
                    primary_player,
                    match,
                    minute,
                    secondary_player,
                    importance='significant' if rivalry.intensity == 'intense' else 'minor',
                    duration=f"{rivalry.interaction_count} encounters"
                )
                if event:
                    events.append(event)
        
        # Проверяем на химию команды
        if secondary_player and primary_player.club == secondary_player.club:
            chemistry = ChemistryCalculator.get_chemistry_between(primary_player, secondary_player)
            if chemistry and chemistry.strength > 0.7:
                event = cls.create_narrative_event(
                    'chemistry_moment',
                    primary_player,
                    match,
                    minute,
                    secondary_player,
                    importance='minor'
                )
                if event:
                    events.append(event)
        
        # Проверяем на рост характера (на основе недавних эволюций)
        recent_evolutions = EvolutionEngine.get_player_evolution_history(primary_player, 1)
        if recent_evolutions and random.random() < 0.1:  # 10% шанс
            event = cls.create_narrative_event(
                'character_growth',
                primary_player,
                match,
                minute,
                importance='minor'
            )
            if event:
                events.append(event)
        
        return events


class NarrativeAIEngine:
    """
    Главный класс для управления всей нарративной системой
    """
    
    @classmethod
    def initialize_club_narratives(cls, club):
        """
        Инициализирует нарративные элементы для клуба
        """
        players = list(club.player_set.all())
        
        if len(players) < 2:
            return {'rivalries': [], 'chemistry': []}
            
        # Генерируем случайные соперничества и химию
        rivalries = RivalryManager.generate_random_rivalries(players, count=2)
        chemistry_bonds = ChemistryCalculator.generate_random_chemistry(players, count=3)
        
        return {
            'rivalries': rivalries,
            'chemistry': chemistry_bonds
        }
    
    @classmethod
    def process_match_event(cls, match, minute, event_type, player, related_player=None):
        """
        Обрабатывает событие матча для нарративной системы
        """
        results = {
            'evolutions': [],
            'narrative_events': [],
            'updated_relationships': []
        }
        
        # Обрабатываем эволюцию характера
        evolutions = EvolutionEngine.evolve_personality(
            player, event_type, match, related_player
        )
        if evolutions:
            results['evolutions'].extend(evolutions)
        
        # Обновляем отношения
        if related_player:
            # Обновляем соперничество если есть
            rivalry = RivalryManager.update_rivalry_interaction(player, related_player)
            if rivalry:
                results['updated_relationships'].append(('rivalry', rivalry))
            
            # Обновляем химию если игроки из одной команды
            if player.club == related_player.club:
                chemistry = ChemistryCalculator.update_chemistry_interaction(player, related_player)
                if chemistry:
                    results['updated_relationships'].append(('chemistry', chemistry))
        
        # Генерируем нарративные события
        narrative_events = NarrativeGenerator.detect_narrative_opportunities(
            match, minute, {'player': player, 'related_player': related_player}
        )
        results['narrative_events'].extend(narrative_events)
        
        return results
    
    @classmethod
    def get_match_narrative_summary(cls, match):
        """
        Возвращает сводку нарративных событий матча
        """
        narrative_events = NarrativeEvent.objects.filter(match=match).order_by('minute')
        evolutions = CharacterEvolution.objects.filter(match=match).order_by('timestamp')
        
        return {
            'narrative_events': narrative_events,
            'character_evolutions': evolutions,
            'total_events': narrative_events.count(),
            'major_events': narrative_events.filter(importance__in=['major', 'legendary']).count()
        }