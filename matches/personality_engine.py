"""
Personality Engine для симуляции футбольного матча.

Модуль обеспечивает интеграцию personality traits игроков с игровой механикой,
влияя на принятие решений, поведение и эффективность действий игроков.

Конфигурация: 40% реализм, 60% геймплей
- Влияния сбалансированы для реалистичности, но приоритет отдается игровому опыту
- Модификаторы в диапазоне -0.25 до +0.25 для плавной интеграции
"""

from django.conf import settings
import logging
import random

logger = logging.getLogger(__name__)


class PersonalityModifier:
    """
    Основной класс для применения personality traits к игровой механике.
    
    Предоставляет статические методы для расчета модификаторов влияния
    personality traits на различные игровые действия.
    """
    
    # Конфигурация влияний personality traits (40% реализм, 60% геймплей)
    TRAIT_INFLUENCES = {
        'aggression': {
            'fouls': 0.15,          # +15% вероятность фолов
            'pressing': 0.10,       # +10% интенсивность прессинга
            'tackles': 0.08,        # +8% агрессивность в отборах
        },
        'confidence': {
            'shot_accuracy': 0.12,  # +12% точность ударов
            'dribbling': 0.10,      # +10% успешность дриблинга
            'penalties': 0.15,      # +15% точность пенальти
            'key_moments': 0.08,    # +8% в ключевых моментах
        },
        'risk_taking': {
            'long_shots': 0.20,     # +20% склонность к дальним ударам
            'long_passes': 0.18,    # +18% склонность к длинным пасам
            'through_balls': 0.15,  # +15% склонность к прострелам
            'solo_runs': 0.12,      # +12% склонность к сольным проходам
        },
        'patience': {
            'pass_accuracy': 0.10,  # +10% точность пасов
            'foul_reduction': -0.15, # -15% склонность к фолам
            'possession_time': 0.08, # +8% время владения мячом
            'shot_selection': 0.12,  # +12% качество выбора момента для удара
        },
        'teamwork': {
            'pass_preference': 0.15, # +15% предпочтение паса перед ударом
            'assist_likelihood': 0.12, # +12% вероятность голевой передачи
            'positioning': 0.10,     # +10% качество позиционирования
            'support_runs': 0.08,    # +8% частота поддерживающих перебежек
        },
        'leadership': {
            'team_morale': 0.05,     # +5% влияние на мораль команды
            'pressure_resistance': 0.08, # +8% устойчивость к давлению
            'crucial_moments': 0.10, # +10% эффективность в решающие моменты
        },
        'ambition': {
            'shot_attempts': 0.08,   # +8% частота ударов
            'forward_runs': 0.10,    # +10% склонность к атакующим перебежкам
            'risk_in_attack': 0.06,  # +6% риск в атаке
        },
        'charisma': {
            'referee_influence': 0.03, # +3% влияние на судейские решения
            'opponent_pressure': 0.05, # +5% психологическое давление на противника
        },
        'endurance': {
            'late_game_performance': 0.12, # +12% эффективность в конце матча
            'stamina_recovery': 0.08,       # +8% восстановление выносливости
        },
        'adaptability': {
            'tactical_changes': 0.08,  # +8% адаптация к тактическим изменениям
            'weather_conditions': 0.06, # +6% адаптация к погодным условиям
        }
    }
    
    @staticmethod
    def _is_personality_enabled():
        """Проверяет, включен ли personality engine в настройках."""
        return getattr(settings, 'USE_PERSONALITY_ENGINE', False)
    
    @staticmethod
    def _normalize_trait_value(trait_value):
        """
        Нормализует значение trait (1-20) в модификатор (-0.25 to +0.25).
        
        Args:
            trait_value (int): Значение trait от 1 до 20
            
        Returns:
            float: Нормализованный модификатор
        """
        if trait_value is None:
            return 0.0
        
        # Преобразуем диапазон 1-20 в -0.25 to +0.25
        # 10.5 - средняя точка, 1 -> -0.25, 20 -> +0.25
        normalized = (trait_value - 10.5) / 38.0  # 38 = (20-1) * 2
        return max(-0.25, min(0.25, normalized))
    
    @staticmethod
    def _get_trait_value(player, trait_name):
        """
        Получает значение указанного personality trait игрока.
        
        Args:
            player: Объект игрока
            trait_name (str): Название trait
            
        Returns:
            int: Значение trait или None если не найдено
        """
        if not player or not hasattr(player, 'personality_traits'):
            return None
        
        personality_traits = player.personality_traits
        if not personality_traits or not isinstance(personality_traits, dict):
            return None
        
        return personality_traits.get(trait_name)
    
    @staticmethod
    def get_foul_modifier(player):
        """
        Вычисляет модификатор склонности к фолам для игрока.
        
        Args:
            player: Объект игрока
            
        Returns:
            float: Модификатор фолов (-0.25 to +0.25)
        """
        if not PersonalityModifier._is_personality_enabled():
            return 0.0
        
        try:
            # Агрессивность увеличивает склонность к фолам
            aggression = PersonalityModifier._get_trait_value(player, 'aggression')
            aggression_modifier = PersonalityModifier._normalize_trait_value(aggression)
            aggression_influence = aggression_modifier * PersonalityModifier.TRAIT_INFLUENCES['aggression']['fouls']
            
            # Терпеливость снижает склонность к фолам
            patience = PersonalityModifier._get_trait_value(player, 'patience')
            patience_modifier = PersonalityModifier._normalize_trait_value(patience)
            patience_influence = patience_modifier * PersonalityModifier.TRAIT_INFLUENCES['patience']['foul_reduction']
            
            total_modifier = aggression_influence + patience_influence
            return max(-0.25, min(0.25, total_modifier))
            
        except Exception as e:
            logger.warning(f"Error calculating foul modifier for player {player.id}: {e}")
            return 0.0
    
    @staticmethod
    def get_pass_modifier(player, context=None):
        """
        Вычисляет модификатор точности и предпочтения пасов для игрока.
        
        Args:
            player: Объект игрока
            context (dict, optional): Контекст игровой ситуации
                - 'pass_type': 'short', 'long', 'through'
                - 'pressure': уровень давления (0.0-1.0)
                - 'time_pressure': временное давление (0.0-1.0)
            
        Returns:
            dict: Модификаторы пасов
                - 'accuracy': модификатор точности
                - 'preference': модификатор предпочтения паса
                - 'risk': модификатор рискованности паса
        """
        if not PersonalityModifier._is_personality_enabled():
            return {'accuracy': 0.0, 'preference': 0.0, 'risk': 0.0}
        
        try:
            context = context or {}
            pass_type = context.get('pass_type', 'short')
            
            # Базовые модификаторы
            result = {'accuracy': 0.0, 'preference': 0.0, 'risk': 0.0}
            
            # Терпеливость улучшает точность пасов
            patience = PersonalityModifier._get_trait_value(player, 'patience')
            if patience:
                patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                result['accuracy'] += patience_modifier * PersonalityModifier.TRAIT_INFLUENCES['patience']['pass_accuracy']
            
            # Командная игра увеличивает предпочтение паса
            teamwork = PersonalityModifier._get_trait_value(player, 'teamwork')
            if teamwork:
                teamwork_modifier = PersonalityModifier._normalize_trait_value(teamwork)
                result['preference'] += teamwork_modifier * PersonalityModifier.TRAIT_INFLUENCES['teamwork']['pass_preference']
            
            # Склонность к риску влияет на выбор типа паса
            risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
            if risk_taking:
                risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                
                if pass_type == 'long':
                    result['preference'] += risk_modifier * PersonalityModifier.TRAIT_INFLUENCES['risk_taking']['long_passes']
                elif pass_type == 'through':
                    result['preference'] += risk_modifier * PersonalityModifier.TRAIT_INFLUENCES['risk_taking']['through_balls']
                
                result['risk'] += risk_modifier
            
            # Ограничиваем значения
            for key in result:
                result[key] = max(-0.25, min(0.25, result[key]))
            
            return result
            
        except Exception as e:
            logger.warning(f"Error calculating pass modifier for player {player.id}: {e}")
            return {'accuracy': 0.0, 'preference': 0.0, 'risk': 0.0}
    
    @staticmethod
    def get_shot_modifier(player, context=None):
        """
        Вычисляет модификатор ударов для игрока.
        
        Args:
            player: Объект игрока
            context (dict, optional): Контекст игровой ситуации
                - 'shot_type': 'close', 'long', 'penalty'
                - 'pressure': уровень давления (0.0-1.0)
                - 'match_minute': минута матча
                - 'score_difference': разность в счете
            
        Returns:
            dict: Модификаторы ударов
                - 'accuracy': модификатор точности
                - 'frequency': модификатор частоты ударов
                - 'power': модификатор силы удара
        """
        if not PersonalityModifier._is_personality_enabled():
            return {'accuracy': 0.0, 'frequency': 0.0, 'power': 0.0}
        
        try:
            context = context or {}
            shot_type = context.get('shot_type', 'close')
            match_minute = context.get('match_minute', 45)
            
            result = {'accuracy': 0.0, 'frequency': 0.0, 'power': 0.0}
            
            # Уверенность улучшает точность ударов
            confidence = PersonalityModifier._get_trait_value(player, 'confidence')
            if confidence:
                confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
                result['accuracy'] += confidence_modifier * PersonalityModifier.TRAIT_INFLUENCES['confidence']['shot_accuracy']
                
                # Особенно важно для пенальти
                if shot_type == 'penalty':
                    result['accuracy'] += confidence_modifier * PersonalityModifier.TRAIT_INFLUENCES['confidence']['penalties']
            
            # Амбициозность увеличивает частоту ударов
            ambition = PersonalityModifier._get_trait_value(player, 'ambition')
            if ambition:
                ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
                result['frequency'] += ambition_modifier * PersonalityModifier.TRAIT_INFLUENCES['ambition']['shot_attempts']
            
            # Склонность к риску для дальних ударов
            risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
            if risk_taking and shot_type == 'long':
                risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                result['frequency'] += risk_modifier * PersonalityModifier.TRAIT_INFLUENCES['risk_taking']['long_shots']
            
            # Выносливость влияет на точность в конце матча
            endurance = PersonalityModifier._get_trait_value(player, 'endurance')
            if endurance and match_minute > 75:
                endurance_modifier = PersonalityModifier._normalize_trait_value(endurance)
                late_game_bonus = endurance_modifier * PersonalityModifier.TRAIT_INFLUENCES['endurance']['late_game_performance']
                result['accuracy'] += late_game_bonus
                result['power'] += late_game_bonus * 0.5  # Половинное влияние на силу
            
            # Ограничиваем значения
            for key in result:
                result[key] = max(-0.25, min(0.25, result[key]))
            
            return result
            
        except Exception as e:
            logger.warning(f"Error calculating shot modifier for player {player.id}: {e}")
            return {'accuracy': 0.0, 'frequency': 0.0, 'power': 0.0}
    
    @staticmethod
    def get_decision_modifier(player, action_type, context=None):
        """
        Вычисляет модификатор выбора действий для игрока.
        
        Args:
            player: Объект игрока
            action_type (str): Тип действия ('pass', 'shoot', 'dribble', 'tackle')
            context (dict, optional): Контекст игровой ситуации
                - 'teammates_nearby': количество партнеров рядом
                - 'opponents_nearby': количество противников рядом
                - 'goal_distance': расстояние до ворот
                - 'match_situation': 'winning', 'losing', 'drawing'
            
        Returns:
            float: Модификатор склонности к выбору действия (-0.25 to +0.25)
        """
        if not PersonalityModifier._is_personality_enabled():
            return 0.0
        
        try:
            context = context or {}
            modifier = 0.0
            
            if action_type == 'pass':
                # Командная игра увеличивает склонность к пасу
                teamwork = PersonalityModifier._get_trait_value(player, 'teamwork')
                if teamwork:
                    teamwork_modifier = PersonalityModifier._normalize_trait_value(teamwork)
                    modifier += teamwork_modifier * PersonalityModifier.TRAIT_INFLUENCES['teamwork']['pass_preference']
                
                # Терпеливость тоже увеличивает склонность к пасу
                patience = PersonalityModifier._get_trait_value(player, 'patience')
                if patience:
                    patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                    modifier += patience_modifier * 0.08  # Дополнительное влияние терпеливости
            
            elif action_type == 'shoot':
                # Амбициозность увеличивает склонность к ударам
                ambition = PersonalityModifier._get_trait_value(player, 'ambition')
                if ambition:
                    ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
                    modifier += ambition_modifier * PersonalityModifier.TRAIT_INFLUENCES['ambition']['shot_attempts']
                
                # Уверенность тоже влияет на склонность к ударам
                confidence = PersonalityModifier._get_trait_value(player, 'confidence')
                if confidence:
                    confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
                    modifier += confidence_modifier * 0.06  # Меньшее влияние чем амбиции
            
            elif action_type == 'dribble':
                # Склонность к риску и уверенность увеличивают дриблинг
                risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
                if risk_taking:
                    risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                    modifier += risk_modifier * PersonalityModifier.TRAIT_INFLUENCES['risk_taking']['solo_runs']
                
                confidence = PersonalityModifier._get_trait_value(player, 'confidence')
                if confidence:
                    confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
                    modifier += confidence_modifier * PersonalityModifier.TRAIT_INFLUENCES['confidence']['dribbling']
            
            elif action_type == 'tackle':
                # Агрессивность увеличивает склонность к отборам
                aggression = PersonalityModifier._get_trait_value(player, 'aggression')
                if aggression:
                    aggression_modifier = PersonalityModifier._normalize_trait_value(aggression)
                    modifier += aggression_modifier * PersonalityModifier.TRAIT_INFLUENCES['aggression']['tackles']
            
            return max(-0.25, min(0.25, modifier))
            
        except Exception as e:
            logger.warning(f"Error calculating decision modifier for player {player.id}, action {action_type}: {e}")
            return 0.0
    
    @staticmethod
    def get_morale_influence(player, team_performance=None):
        """
        Вычисляет влияние personality traits на мораль игрока и команды.
        
        Args:
            player: Объект игрока
            team_performance (dict, optional): Показатели команды
                - 'recent_results': список последних результатов
                - 'current_score': текущий счет
                - 'match_events': важные события матча
            
        Returns:
            dict: Влияние на мораль
                - 'self_morale': влияние на собственную мораль
                - 'team_morale': влияние на мораль команды
        """
        if not PersonalityModifier._is_personality_enabled():
            return {'self_morale': 0.0, 'team_morale': 0.0}
        
        try:
            result = {'self_morale': 0.0, 'team_morale': 0.0}
            
            # Лидерство влияет на мораль команды
            leadership = PersonalityModifier._get_trait_value(player, 'leadership')
            if leadership:
                leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
                result['team_morale'] += leadership_modifier * PersonalityModifier.TRAIT_INFLUENCES['leadership']['team_morale']
            
            # Харизма тоже влияет на команду
            charisma = PersonalityModifier._get_trait_value(player, 'charisma')
            if charisma:
                charisma_modifier = PersonalityModifier._normalize_trait_value(charisma)
                result['team_morale'] += charisma_modifier * 0.03  # Дополнительное влияние харизмы
            
            # Уверенность влияет на собственную мораль
            confidence = PersonalityModifier._get_trait_value(player, 'confidence')
            if confidence:
                confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
                result['self_morale'] += confidence_modifier * 0.08
            
            # Ограничиваем значения
            for key in result:
                result[key] = max(-0.15, min(0.15, result[key]))  # Меньший диапазон для морали
            
            return result
            
        except Exception as e:
            logger.warning(f"Error calculating morale influence for player {player.id}: {e}")
            return {'self_morale': 0.0, 'team_morale': 0.0}
    
    @staticmethod
    def get_adaptation_modifier(player, situation_context):
        """
        Вычисляет модификатор адаптации к изменениям в игре.
        
        Args:
            player: Объект игрока
            situation_context (dict): Контекст изменений
                - 'tactical_change': изменение тактики
                - 'weather_change': изменение погоды
                - 'opponent_strategy': изменение стратегии противника
                - 'match_phase': фаза матча
            
        Returns:
            float: Модификатор адаптации (-0.15 to +0.15)
        """
        if not PersonalityModifier._is_personality_enabled():
            return 0.0
        
        try:
            modifier = 0.0
            
            # Адаптивность - основной фактор
            adaptability = PersonalityModifier._get_trait_value(player, 'adaptability')
            if adaptability:
                adaptability_modifier = PersonalityModifier._normalize_trait_value(adaptability)
                
                if 'tactical_change' in situation_context:
                    modifier += adaptability_modifier * PersonalityModifier.TRAIT_INFLUENCES['adaptability']['tactical_changes']
                
                if 'weather_change' in situation_context:
                    modifier += adaptability_modifier * PersonalityModifier.TRAIT_INFLUENCES['adaptability']['weather_conditions']
            
            # Лидерство помогает в адаптации
            leadership = PersonalityModifier._get_trait_value(player, 'leadership')
            if leadership:
                leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
                modifier += leadership_modifier * 0.04  # Дополнительное влияние лидерства
            
            return max(-0.15, min(0.15, modifier))
            
        except Exception as e:
            logger.warning(f"Error calculating adaptation modifier for player {player.id}: {e}")
            return 0.0


class PersonalityDecisionEngine:
    """
    Движок принятия решений игроков на основе personality traits.
    
    Обеспечивает контекстно-зависимое принятие решений игроками,
    учитывая их личностные характеристики, игровую ситуацию и стресс.
    
    Конфигурация: 40% реализм, 60% геймплей
    - Решения влияют на игровой процесс, но остаются сбалансированными
    - Модификаторы накладываются на базовую логику принятия решений
    """
    
    # Базовые вероятности действий (без personality влияний)
    BASE_ACTION_PROBABILITIES = {
        'pass': 0.40,       # Базовая склонность к пасу
        'shoot': 0.15,      # Базовая склонность к удару
        'dribble': 0.20,    # Базовая склонность к дриблингу
        'tackle': 0.25,     # Базовая склонность к отбору (для защиты)
    }
    
    # Пороги для различных решений
    DECISION_THRESHOLDS = {
        'risky_action': 0.60,       # Порог для рискованных действий
        'shot_timing': 0.50,        # Порог для времени удара
        'pass_confidence': 0.40,    # Минимальная уверенность для паса
        'pressure_resistance': 0.70, # Порог устойчивости к давлению
    }
    
    @staticmethod
    def choose_action_type(player, context=None):
        """
        Выбирает тип действия для игрока на основе personality traits и контекста.
        
        Args:
            player: Объект игрока
            context (dict, optional): Контекст игровой ситуации
                - 'position': позиция на поле (x, y)
                - 'teammates_nearby': количество партнеров рядом
                - 'opponents_nearby': количество противников рядом
                - 'goal_distance': расстояние до ворот
                - 'match_minute': минута матча
                - 'score_difference': разность в счете
                - 'possession_type': 'attack', 'midfield', 'defense'
                - 'pressure_level': уровень давления (0.0-1.0)
            
        Returns:
            str: Выбранное действие ('pass', 'shoot', 'dribble', 'tackle')
        
        Examples:
            >>> context = {
            ...     'goal_distance': 20,
            ...     'teammates_nearby': 2,
            ...     'opponents_nearby': 1,
            ...     'possession_type': 'attack'
            ... }
            >>> action = PersonalityDecisionEngine.choose_action_type(player, context)
            >>> print(action)  # 'shoot' или 'pass' в зависимости от personality
        """
        context = context or {}
        
        # Базовые вероятности
        probabilities = PersonalityDecisionEngine.BASE_ACTION_PROBABILITIES.copy()
        
        # Корректировка на основе позиции
        possession_type = context.get('possession_type', 'midfield')
        if possession_type == 'attack':
            probabilities['shoot'] += 0.15
            probabilities['pass'] -= 0.05
            probabilities['dribble'] += 0.10
            probabilities['tackle'] -= 0.20
        elif possession_type == 'defense':
            probabilities['tackle'] += 0.20
            probabilities['pass'] += 0.10
            probabilities['shoot'] -= 0.15
            probabilities['dribble'] -= 0.15
        
        # Применяем personality модификаторы
        for action in probabilities:
            personality_modifier = PersonalityModifier.get_decision_modifier(player, action, context)
            probabilities[action] += personality_modifier
        
        # Корректировка на основе контекста
        goal_distance = context.get('goal_distance', 50)
        teammates_nearby = context.get('teammates_nearby', 1)
        opponents_nearby = context.get('opponents_nearby', 1)
        
        # Близость к воротам увеличивает склонность к удару
        if goal_distance < 25:
            probabilities['shoot'] += 0.20
        elif goal_distance < 40:
            probabilities['shoot'] += 0.10
        
        # Много партнеров рядом - больше пасов
        if teammates_nearby >= 3:
            probabilities['pass'] += 0.15
        
        # Много противников - меньше дриблинга
        if opponents_nearby >= 2:
            probabilities['dribble'] -= 0.15
            probabilities['tackle'] += 0.10
        
        # Нормализуем вероятности
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: max(0.0, v/total) for k, v in probabilities.items()}
        
        # Выбираем действие на основе вероятностей
        rand_value = random.random()
        cumulative = 0.0
        
        for action, probability in probabilities.items():
            cumulative += probability
            if rand_value <= cumulative:
                return action
        
        # Fallback - возвращаем действие с наибольшей вероятностью
        return max(probabilities, key=probabilities.get)
    
    @staticmethod
    def should_attempt_risky_action(player, risk_level, context=None):
        """
        Определяет, должен ли игрок предпринять рискованное действие.
        
        Args:
            player: Объект игрока
            risk_level (float): Уровень риска действия (0.0-1.0)
            context (dict, optional): Контекст ситуации
                - 'match_minute': минута матча
                - 'score_difference': разность в счете
                - 'pressure_level': уровень давления
                - 'team_situation': 'winning', 'losing', 'drawing'
                - 'importance': важность ситуации (0.0-1.0)
            
        Returns:
            bool: True если стоит рисковать, False если нет
        
        Examples:
            >>> context = {
            ...     'score_difference': -1,  # Проигрываем
            ...     'match_minute': 85,      # Конец матча
            ...     'importance': 0.9        # Важная ситуация
            ... }
            >>> should_risk = PersonalityDecisionEngine.should_attempt_risky_action(
            ...     player, 0.7, context
            ... )
            >>> print(should_risk)  # True если игрок склонен к риску
        """
        context = context or {}
        
        # Базовый порог риска
        base_threshold = PersonalityDecisionEngine.DECISION_THRESHOLDS['risky_action']
        
        # Получаем personality модификаторы
        risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
        confidence = PersonalityModifier._get_trait_value(player, 'confidence')
        patience = PersonalityModifier._get_trait_value(player, 'patience')
        
        # Рассчитываем склонность к риску
        risk_tendency = 0.5  # Нейтральная базовая склонность
        
        if risk_taking:
            risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
            risk_tendency += risk_modifier * 0.4  # Сильное влияние
        
        if confidence:
            confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
            risk_tendency += confidence_modifier * 0.2  # Умеренное влияние
        
        if patience:
            patience_modifier = PersonalityModifier._normalize_trait_value(patience)
            risk_tendency -= patience_modifier * 0.3  # Снижает склонность к риску
        
        # Корректировки на основе контекста
        match_minute = context.get('match_minute', 45)
        score_difference = context.get('score_difference', 0)
        team_situation = context.get('team_situation', 'drawing')
        importance = context.get('importance', 0.5)
        
        # В конце матча при проигрыше - больше риска
        if match_minute > 75 and (score_difference < 0 or team_situation == 'losing'):
            risk_tendency += 0.25
        
        # В важных ситуациях - больше риска
        risk_tendency += importance * 0.15
        
        # При большом давлении - меньше риска (кроме очень уверенных игроков)
        pressure_level = context.get('pressure_level', 0.5)
        if pressure_level > 0.7:
            pressure_resistance = PersonalityModifier._get_trait_value(player, 'leadership')
            if pressure_resistance:
                resistance_modifier = PersonalityModifier._normalize_trait_value(pressure_resistance)
                pressure_penalty = 0.2 - (resistance_modifier * 0.15)
            else:
                pressure_penalty = 0.2
            risk_tendency -= pressure_penalty
        
        # Ограничиваем значения
        risk_tendency = max(0.0, min(1.0, risk_tendency))
        
        # Сравниваем с уровнем риска действия
        return risk_tendency > (base_threshold + risk_level * 0.3)
    
    @staticmethod
    def evaluate_passing_options(player, passing_options, context=None):
        """
        Оценивает варианты пасов и выбирает наилучший на основе personality.
        
        Args:
            player: Объект игрока
            passing_options (list): Список вариантов паса
                Каждый элемент - dict с ключами:
                - 'target_player': целевой игрок
                - 'success_probability': вероятность успеха (0.0-1.0)
                - 'risk_level': уровень риска (0.0-1.0)
                - 'pass_type': 'short', 'long', 'through'
                - 'potential_benefit': потенциальная польза (0.0-1.0)
            context (dict, optional): Контекст ситуации
                - 'pressure_level': уровень давления
                - 'time_remaining': оставшееся время
                - 'team_strategy': стратегия команды
            
        Returns:
            dict: Выбранный вариант паса или None если нет подходящих
        
        Examples:
            >>> options = [
            ...     {
            ...         'target_player': teammate1,
            ...         'success_probability': 0.8,
            ...         'risk_level': 0.3,
            ...         'pass_type': 'short',
            ...         'potential_benefit': 0.5
            ...     },
            ...     {
            ...         'target_player': teammate2,
            ...         'success_probability': 0.6,
            ...         'risk_level': 0.7,
            ...         'pass_type': 'through',
            ...         'potential_benefit': 0.9
            ...     }
            ... ]
            >>> best_pass = PersonalityDecisionEngine.evaluate_passing_options(
            ...     player, options, context
            ... )
        """
        if not passing_options:
            return None
        
        context = context or {}
        
        # Получаем personality traits
        teamwork = PersonalityModifier._get_trait_value(player, 'teamwork')
        risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
        patience = PersonalityModifier._get_trait_value(player, 'patience')
        confidence = PersonalityModifier._get_trait_value(player, 'confidence')
        
        # Веса для оценки пасов
        weights = {
            'success_probability': 0.4,  # Базовый вес для вероятности успеха
            'potential_benefit': 0.3,    # Вес для потенциальной пользы
            'risk_penalty': 0.2,         # Штраф за риск
            'pass_type_preference': 0.1  # Предпочтение типа паса
        }
        
        # Корректируем веса на основе personality
        if teamwork:
            teamwork_modifier = PersonalityModifier._normalize_trait_value(teamwork)
            weights['success_probability'] += teamwork_modifier * 0.15  # Командные игроки ценят надежность
        
        if risk_taking:
            risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
            weights['potential_benefit'] += risk_modifier * 0.2   # Рискованные игроки ценят пользу
            weights['risk_penalty'] -= risk_modifier * 0.15      # Меньше боятся риска
        
        if patience:
            patience_modifier = PersonalityModifier._normalize_trait_value(patience)
            weights['success_probability'] += patience_modifier * 0.1  # Терпеливые ценят надежность
        
        if confidence:
            confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
            weights['risk_penalty'] -= confidence_modifier * 0.1  # Уверенные меньше боятся риска
        
        # Оцениваем каждый вариант
        scored_options = []
        for option in passing_options:
            score = 0.0
            
            # Базовая оценка
            score += option.get('success_probability', 0.0) * weights['success_probability']
            score += option.get('potential_benefit', 0.0) * weights['potential_benefit']
            score -= option.get('risk_level', 0.0) * weights['risk_penalty']
            
            # Предпочтение типа паса
            pass_type = option.get('pass_type', 'short')
            type_preference = 0.0
            
            if pass_type == 'short' and patience:
                patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                type_preference = patience_modifier * 0.2
            elif pass_type in ['long', 'through'] and risk_taking:
                risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                type_preference = risk_modifier * 0.15
            
            score += type_preference * weights['pass_type_preference']
            
            # Корректировки на основе контекста
            pressure_level = context.get('pressure_level', 0.5)
            if pressure_level > 0.7 and option.get('pass_type') == 'short':
                score += 0.1  # Под давлением предпочитаем простые пасы
            
            scored_options.append((option, score))
        
        # Сортируем по оценке
        scored_options.sort(key=lambda x: x[1], reverse=True)
        
        # Проверяем минимальный порог уверенности
        best_option, best_score = scored_options[0]
        min_confidence = PersonalityDecisionEngine.DECISION_THRESHOLDS['pass_confidence']
        
        if best_score >= min_confidence:
            return best_option
        
        return None
    
    @staticmethod
    def decide_shot_timing(player, shot_opportunity, context=None):
        """
        Принимает решение о времени удара на основе personality и ситуации.
        
        Args:
            player: Объект игрока
            shot_opportunity (dict): Информация о возможности удара
                - 'success_probability': вероятность попадания (0.0-1.0)
                - 'goal_distance': расстояние до ворот
                - 'angle': угол к воротам
                - 'pressure_level': уровень давления
                - 'shot_type': 'close', 'long', 'header', 'volley'
            context (dict, optional): Дополнительный контекст
                - 'alternative_actions': альтернативные действия
                - 'match_minute': минута матча
                - 'score_difference': разность в счете
                - 'team_momentum': импульс команды
            
        Returns:
            str: Решение ('shoot_now', 'wait_for_better', 'pass_instead')
        
        Examples:
            >>> opportunity = {
            ...     'success_probability': 0.3,
            ...     'goal_distance': 25,
            ...     'pressure_level': 0.6,
            ...     'shot_type': 'long'
            ... }
            >>> context = {
            ...     'score_difference': -1,
            ...     'match_minute': 80
            ... }
            >>> decision = PersonalityDecisionEngine.decide_shot_timing(
            ...     player, opportunity, context
            ... )
        """
        context = context or {}
        
        # Получаем personality traits
        ambition = PersonalityModifier._get_trait_value(player, 'ambition')
        patience = PersonalityModifier._get_trait_value(player, 'patience')
        confidence = PersonalityModifier._get_trait_value(player, 'confidence')
        risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
        
        # Базовая оценка возможности удара
        shot_quality = shot_opportunity.get('success_probability', 0.0)
        base_threshold = PersonalityDecisionEngine.DECISION_THRESHOLDS['shot_timing']
        
        # Корректируем порог на основе personality
        threshold = base_threshold
        
        if ambition:
            ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
            threshold -= ambition_modifier * 0.2  # Амбициозные стреляют при меньших шансах
        
        if patience:
            patience_modifier = PersonalityModifier._normalize_trait_value(patience)
            threshold += patience_modifier * 0.15  # Терпеливые ждут лучших моментов
        
        if confidence:
            confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
            # Уверенные игроки корректируют воспринимаемое качество удара
            shot_quality += confidence_modifier * 0.1
        
        # Контекстные факторы
        match_minute = context.get('match_minute', 45)
        score_difference = context.get('score_difference', 0)
        pressure_level = shot_opportunity.get('pressure_level', 0.5)
        shot_type = shot_opportunity.get('shot_type', 'close')
        
        # В конце матча при проигрыше - стреляем чаще
        if match_minute > 70 and score_difference < 0:
            urgency_factor = (match_minute - 70) / 20.0  # Увеличивается к концу
            threshold -= urgency_factor * 0.3
        
        # При высоком давлении - быстрее принимаем решение
        if pressure_level > 0.7:
            threshold -= 0.1
        
        # Специальные случаи для типов ударов
        if shot_type == 'long' and risk_taking:
            risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
            threshold -= risk_modifier * 0.1  # Любители риска чаще бьют издалека
        
        # Принимаем решение
        if shot_quality >= threshold:
            return 'shoot_now'
        elif shot_quality >= threshold - 0.2:
            # Близко к порогу - проверяем альтернативы
            alternatives = context.get('alternative_actions', [])
            
            # Если есть хорошие альтернативы и игрок терпелив - ждем
            if alternatives and patience:
                patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                if patience_modifier > 0.1:
                    return 'wait_for_better'
            
            return 'shoot_now'
        else:
            # Низкое качество удара
            if ambition:
                ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
                # Очень амбициозные могут стрелять даже при низких шансах
                if ambition_modifier > 0.15 and random.random() < 0.3:
                    return 'shoot_now'
            
            return 'pass_instead'
    
    @staticmethod
    def get_decision_confidence(player, action_type, context=None):
        """
        Вычисляет уверенность игрока в принятом решении.
        
        Args:
            player: Объект игрока
            action_type (str): Тип действия
            context (dict, optional): Контекст ситуации
                - 'situation_familiarity': знакомость с ситуацией (0.0-1.0)
                - 'pressure_level': уровень давления
                - 'support_level': уровень поддержки команды
                - 'match_importance': важность матча
            
        Returns:
            float: Уровень уверенности в решении (0.0-1.0)
        
        Examples:
            >>> context = {
            ...     'situation_familiarity': 0.8,
            ...     'pressure_level': 0.3,
            ...     'support_level': 0.7
            ... }
            >>> confidence = PersonalityDecisionEngine.get_decision_confidence(
            ...     player, 'shoot', context
            ... )
            >>> print(f"Confidence: {confidence:.2f}")
        """
        context = context or {}
        
        # Базовая уверенность
        base_confidence = 0.5
        
        # Получаем personality traits
        confidence_trait = PersonalityModifier._get_trait_value(player, 'confidence')
        leadership = PersonalityModifier._get_trait_value(player, 'leadership')
        experience = PersonalityModifier._get_trait_value(player, 'adaptability')
        
        # Основные модификаторы уверенности
        if confidence_trait:
            confidence_modifier = PersonalityModifier._normalize_trait_value(confidence_trait)
            base_confidence += confidence_modifier * 0.3  # Сильное влияние
        
        if leadership:
            leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
            base_confidence += leadership_modifier * 0.15  # Лидеры более уверены
        
        if experience:
            experience_modifier = PersonalityModifier._normalize_trait_value(experience)
            base_confidence += experience_modifier * 0.1  # Опыт добавляет уверенности
        
        # Контекстные факторы
        situation_familiarity = context.get('situation_familiarity', 0.5)
        pressure_level = context.get('pressure_level', 0.5)
        support_level = context.get('support_level', 0.5)
        match_importance = context.get('match_importance', 0.5)
        
        # Знакомость с ситуацией увеличивает уверенность
        base_confidence += (situation_familiarity - 0.5) * 0.2
        
        # Давление снижает уверенность (кроме стрессоустойчивых)
        pressure_penalty = (pressure_level - 0.5) * 0.25
        if leadership:
            leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
            pressure_penalty *= (1.0 - leadership_modifier * 0.5)  # Лидеры лучше справляются с давлением
        base_confidence -= pressure_penalty
        
        # Поддержка команды увеличивает уверенность
        base_confidence += (support_level - 0.5) * 0.15
        
        # Важность матча может как увеличивать, так и снижать уверенность
        if match_importance > 0.7:
            if confidence_trait and PersonalityModifier._normalize_trait_value(confidence_trait) > 0.1:
                base_confidence += 0.1  # Уверенные игроки мотивируются важностью
            else:
                base_confidence -= 0.1  # Неуверенные игроки нервничают
        
        # Специфические модификаторы для типов действий
        if action_type == 'shoot':
            shot_modifier = PersonalityModifier.get_shot_modifier(player, context)
            base_confidence += shot_modifier.get('accuracy', 0.0) * 0.5
        elif action_type == 'pass':
            pass_modifier = PersonalityModifier.get_pass_modifier(player, context)
            base_confidence += pass_modifier.get('accuracy', 0.0) * 0.5
        elif action_type == 'dribble':
            if confidence_trait:
                dribble_bonus = PersonalityModifier._normalize_trait_value(confidence_trait) * 0.1
                base_confidence += dribble_bonus
        
        # Ограничиваем значения
        return max(0.0, min(1.0, base_confidence))
    
    @staticmethod
    def evaluate_tactical_decision(player, tactical_options, context=None):
        """
        Оценивает тактические решения игрока в сложных ситуациях.
        
        Args:
            player: Объект игрока
            tactical_options (list): Список тактических вариантов
                Каждый элемент - dict с ключами:
                - 'option_type': тип варианта
                - 'success_probability': вероятность успеха
                - 'risk_level': уровень риска
                - 'team_benefit': польза для команды
                - 'personal_benefit': личная польза
            context (dict, optional): Тактический контекст
                - 'team_strategy': стратегия команды
                - 'opponent_weakness': слабость противника
                - 'match_phase': фаза матча
                - 'score_situation': ситуация со счетом
        
        Returns:
            dict: Выбранный тактический вариант
        
        Examples:
            >>> options = [
            ...     {
            ...         'option_type': 'conservative_play',
            ...         'success_probability': 0.8,
            ...         'risk_level': 0.2,
            ...         'team_benefit': 0.6,
            ...         'personal_benefit': 0.4
            ...     },
            ...     {
            ...         'option_type': 'aggressive_press',
            ...         'success_probability': 0.6,
            ...         'risk_level': 0.7,
            ...         'team_benefit': 0.8,
            ...         'personal_benefit': 0.3
            ...     }
            ... ]
            >>> choice = PersonalityDecisionEngine.evaluate_tactical_decision(
            ...     player, options, context
            ... )
        """
        if not tactical_options:
            return None
        
        context = context or {}
        
        # Получаем ключевые personality traits для тактических решений
        teamwork = PersonalityModifier._get_trait_value(player, 'teamwork')
        ambition = PersonalityModifier._get_trait_value(player, 'ambition')
        risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
        leadership = PersonalityModifier._get_trait_value(player, 'leadership')
        patience = PersonalityModifier._get_trait_value(player, 'patience')
        
        # Веса для оценки тактических решений
        weights = {
            'success_probability': 0.3,
            'team_benefit': 0.25,
            'personal_benefit': 0.15,
            'risk_factor': 0.2,
            'leadership_factor': 0.1
        }
        
        # Корректируем веса на основе personality
        if teamwork:
            teamwork_modifier = PersonalityModifier._normalize_trait_value(teamwork)
            weights['team_benefit'] += teamwork_modifier * 0.15
            weights['personal_benefit'] -= teamwork_modifier * 0.1
        
        if ambition:
            ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
            weights['personal_benefit'] += ambition_modifier * 0.1
        
        if leadership:
            leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
            weights['leadership_factor'] += leadership_modifier * 0.15
            weights['team_benefit'] += leadership_modifier * 0.1
        
        # Оцениваем каждый тактический вариант
        scored_options = []
        for option in tactical_options:
            score = 0.0
            
            # Базовые факторы
            score += option.get('success_probability', 0.0) * weights['success_probability']
            score += option.get('team_benefit', 0.0) * weights['team_benefit']
            score += option.get('personal_benefit', 0.0) * weights['personal_benefit']
            
            # Фактор риска (может быть как положительным, так и отрицательным)
            risk_level = option.get('risk_level', 0.0)
            if risk_taking:
                risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                risk_impact = risk_modifier * risk_level * weights['risk_factor']
            else:
                risk_impact = -risk_level * weights['risk_factor']  # Штраф за риск
            score += risk_impact
            
            # Лидерские решения
            if leadership and option.get('option_type') in ['lead_by_example', 'organize_team', 'motivate_teammates']:
                leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
                score += leadership_modifier * weights['leadership_factor']
            
            # Контекстные корректировки
            match_phase = context.get('match_phase', 'middle')
            score_situation = context.get('score_situation', 'drawing')
            
            if match_phase == 'late' and score_situation == 'losing':
                if option.get('option_type') in ['aggressive_press', 'risky_attack']:
                    score += 0.15  # Бонус за агрессивные действия при проигрыше
            
            if patience and option.get('option_type') in ['patient_buildup', 'wait_for_opportunity']:
                patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                score += patience_modifier * 0.1
            
            scored_options.append((option, score))
        
        # Выбираем лучший вариант
        scored_options.sort(key=lambda x: x[1], reverse=True)
        return scored_options[0][0] if scored_options else None
    
    @staticmethod
    def get_influencing_trait(player, action_type, context=None):
        """
        Определяет основную черту характера, влияющую на принятое решение.
        
        Args:
            player: Объект игрока
            action_type (str): Тип действия ('pass', 'shoot', 'dribble', 'tackle', 'long_pass', 'attack')
            context (dict, optional): Контекст игровой ситуации
            
        Returns:
            tuple: (trait_name, trait_description) или (None, None) если нет влияния
        """
        if not getattr(settings, 'USE_PERSONALITY_ENGINE', False):
            return (None, None)
        
        try:
            # Словарь с описаниями черт характера на русском
            TRAIT_DESCRIPTIONS = {
                'aggression': 'Агрессивность',
                'confidence': 'Уверенность',
                'risk_taking': 'Склонность к риску',
                'patience': 'Терпеливость',
                'teamwork': 'Командная игра',
                'leadership': 'Лидерство',
                'ambition': 'Амбициозность',
                'charisma': 'Харизма',
                'endurance': 'Выносливость',
                'adaptability': 'Адаптивность'
            }
            
            # Определяем основную черту для каждого типа действия
            trait_mapping = {
                'shoot': ['ambition', 'confidence', 'risk_taking'],
                'pass': ['teamwork', 'patience'],
                'long_pass': ['risk_taking', 'ambition'],
                'dribble': ['confidence', 'risk_taking'],
                'tackle': ['aggression'],
                'attack': ['ambition', 'risk_taking']
            }
            
            # Получаем черты для данного действия
            relevant_traits = trait_mapping.get(action_type, [])
            if not relevant_traits:
                return (None, None)
            
            # Находим черту с наибольшим значением у игрока
            max_trait = None
            max_value = 0
            
            for trait in relevant_traits:
                trait_value = PersonalityModifier._get_trait_value(player, trait)
                if trait_value and trait_value > max_value:
                    max_value = trait_value
                    max_trait = trait
            
            # Возвращаем черту только если её значение достаточно высокое (>12)
            if max_trait and max_value > 12:
                return (max_trait, TRAIT_DESCRIPTIONS.get(max_trait, max_trait))
            
            return (None, None)
            
        except Exception as e:
            logger.warning(f"Error getting influencing trait for player {player.id}: {e}")
            return (None, None)