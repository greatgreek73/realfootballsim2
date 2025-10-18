"""
Personality Engine ╨┤╨╗╤П ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╨╕ ╤Д╤Г╤В╨▒╨╛╨╗╤М╨╜╨╛╨│╨╛ ╨╝╨░╤В╤З╨░.

╨Ь╨╛╨┤╤Г╨╗╤М ╨╛╨▒╨╡╤Б╨┐╨╡╤З╨╕╨▓╨░╨╡╤В ╨╕╨╜╤В╨╡╨│╤А╨░╤Ж╨╕╤О personality traits ╨╕╨│╤А╨╛╨║╨╛╨▓ ╤Б ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╨╝╨╡╤Е╨░╨╜╨╕╨║╨╛╨╣,
╨▓╨╗╨╕╤П╤П ╨╜╨░ ╨┐╤А╨╕╨╜╤П╤В╨╕╨╡ ╤А╨╡╤И╨╡╨╜╨╕╨╣, ╨┐╨╛╨▓╨╡╨┤╨╡╨╜╨╕╨╡ ╨╕ ╤Н╤Д╤Д╨╡╨║╤В╨╕╨▓╨╜╨╛╤Б╤В╤М ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╣ ╨╕╨│╤А╨╛╨║╨╛╨▓.

╨Ъ╨╛╨╜╤Д╨╕╨│╤Г╤А╨░╤Ж╨╕╤П: 40% ╤А╨╡╨░╨╗╨╕╨╖╨╝, 60% ╨│╨╡╨╣╨╝╨┐╨╗╨╡╨╣
- ╨Т╨╗╨╕╤П╨╜╨╕╤П ╤Б╨▒╨░╨╗╨░╨╜╤Б╨╕╤А╨╛╨▓╨░╨╜╤Л ╨┤╨╗╤П ╤А╨╡╨░╨╗╨╕╤Б╤В╨╕╤З╨╜╨╛╤Б╤В╨╕, ╨╜╨╛ ╨┐╤А╨╕╨╛╤А╨╕╤В╨╡╤В ╨╛╤В╨┤╨░╨╡╤В╤Б╤П ╨╕╨│╤А╨╛╨▓╨╛╨╝╤Г ╨╛╨┐╤Л╤В╤Г
- ╨Ь╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л ╨▓ ╨┤╨╕╨░╨┐╨░╨╖╨╛╨╜╨╡ -0.25 ╨┤╨╛ +0.25 ╨┤╨╗╤П ╨┐╨╗╨░╨▓╨╜╨╛╨╣ ╨╕╨╜╤В╨╡╨│╤А╨░╤Ж╨╕╨╕
"""

from django.conf import settings
import logging
import random

logger = logging.getLogger(__name__)


class PersonalityModifier:
    """
    ╨Ю╤Б╨╜╨╛╨▓╨╜╨╛╨╣ ╨║╨╗╨░╤Б╤Б ╨┤╨╗╤П ╨┐╤А╨╕╨╝╨╡╨╜╨╡╨╜╨╕╤П personality traits ╨║ ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╨╝╨╡╤Е╨░╨╜╨╕╨║╨╡.
    
    ╨Я╤А╨╡╨┤╨╛╤Б╤В╨░╨▓╨╗╤П╨╡╤В ╤Б╤В╨░╤В╨╕╤З╨╡╤Б╨║╨╕╨╡ ╨╝╨╡╤В╨╛╨┤╤Л ╨┤╨╗╤П ╤А╨░╤Б╤З╨╡╤В╨░ ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╨╛╨▓ ╨▓╨╗╨╕╤П╨╜╨╕╤П
    personality traits ╨╜╨░ ╤А╨░╨╖╨╗╨╕╤З╨╜╤Л╨╡ ╨╕╨│╤А╨╛╨▓╤Л╨╡ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П.
    """
    
    # ╨Ъ╨╛╨╜╤Д╨╕╨│╤Г╤А╨░╤Ж╨╕╤П ╨▓╨╗╨╕╤П╨╜╨╕╨╣ personality traits (40% ╤А╨╡╨░╨╗╨╕╨╖╨╝, 60% ╨│╨╡╨╣╨╝╨┐╨╗╨╡╨╣)
    TRAIT_INFLUENCES = {
        'aggression': {
            'fouls': 0.15,          # +15% ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╤М ╤Д╨╛╨╗╨╛╨▓
            'pressing': 0.10,       # +10% ╨╕╨╜╤В╨╡╨╜╤Б╨╕╨▓╨╜╨╛╤Б╤В╤М ╨┐╤А╨╡╤Б╤Б╨╕╨╜╨│╨░
            'tackles': 0.08,        # +8% ╨░╨│╤А╨╡╤Б╤Б╨╕╨▓╨╜╨╛╤Б╤В╤М ╨▓ ╨╛╤В╨▒╨╛╤А╨░╤Е
        },
        'confidence': {
            'shot_accuracy': 0.12,  # +12% ╤В╨╛╤З╨╜╨╛╤Б╤В╤М ╤Г╨┤╨░╤А╨╛╨▓
            'dribbling': 0.10,      # +10% ╤Г╤Б╨┐╨╡╤И╨╜╨╛╤Б╤В╤М ╨┤╤А╨╕╨▒╨╗╨╕╨╜╨│╨░
            'penalties': 0.15,      # +15% ╤В╨╛╤З╨╜╨╛╤Б╤В╤М ╨┐╨╡╨╜╨░╨╗╤М╤В╨╕
            'key_moments': 0.08,    # +8% ╨▓ ╨║╨╗╤О╤З╨╡╨▓╤Л╤Е ╨╝╨╛╨╝╨╡╨╜╤В╨░╤Е
        },
        'risk_taking': {
            'long_shots': 0.20,     # +20% ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨┤╨░╨╗╤М╨╜╨╕╨╝ ╤Г╨┤╨░╤А╨░╨╝
            'long_passes': 0.18,    # +18% ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨┤╨╗╨╕╨╜╨╜╤Л╨╝ ╨┐╨░╤Б╨░╨╝
            'through_balls': 0.15,  # +15% ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨┐╤А╨╛╤Б╤В╤А╨╡╨╗╨░╨╝
            'solo_runs': 0.12,      # +12% ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤Б╨╛╨╗╤М╨╜╤Л╨╝ ╨┐╤А╨╛╤Е╨╛╨┤╨░╨╝
        },
        'patience': {
            'pass_accuracy': 0.10,  # +10% ╤В╨╛╤З╨╜╨╛╤Б╤В╤М ╨┐╨░╤Б╨╛╨▓
            'foul_reduction': -0.15, # -15% ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤Д╨╛╨╗╨░╨╝
            'possession_time': 0.08, # +8% ╨▓╤А╨╡╨╝╤П ╨▓╨╗╨░╨┤╨╡╨╜╨╕╤П ╨╝╤П╤З╨╛╨╝
            'shot_selection': 0.12,  # +12% ╨║╨░╤З╨╡╤Б╤В╨▓╨╛ ╨▓╤Л╨▒╨╛╤А╨░ ╨╝╨╛╨╝╨╡╨╜╤В╨░ ╨┤╨╗╤П ╤Г╨┤╨░╤А╨░
        },
        'teamwork': {
            'pass_preference': 0.15, # +15% ╨┐╤А╨╡╨┤╨┐╨╛╤З╤В╨╡╨╜╨╕╨╡ ╨┐╨░╤Б╨░ ╨┐╨╡╤А╨╡╨┤ ╤Г╨┤╨░╤А╨╛╨╝
            'assist_likelihood': 0.12, # +12% ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╤М ╨│╨╛╨╗╨╡╨▓╨╛╨╣ ╨┐╨╡╤А╨╡╨┤╨░╤З╨╕
            'positioning': 0.10,     # +10% ╨║╨░╤З╨╡╤Б╤В╨▓╨╛ ╨┐╨╛╨╖╨╕╤Ж╨╕╨╛╨╜╨╕╤А╨╛╨▓╨░╨╜╨╕╤П
            'support_runs': 0.08,    # +8% ╤З╨░╤Б╤В╨╛╤В╨░ ╨┐╨╛╨┤╨┤╨╡╤А╨╢╨╕╨▓╨░╤О╤Й╨╕╤Е ╨┐╨╡╤А╨╡╨▒╨╡╨╢╨╡╨║
        },
        'leadership': {
            'team_morale': 0.05,     # +5% ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╨╜╨░ ╨╝╨╛╤А╨░╨╗╤М ╨║╨╛╨╝╨░╨╜╨┤╤Л
            'pressure_resistance': 0.08, # +8% ╤Г╤Б╤В╨╛╨╣╤З╨╕╨▓╨╛╤Б╤В╤М ╨║ ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤О
            'crucial_moments': 0.10, # +10% ╤Н╤Д╤Д╨╡╨║╤В╨╕╨▓╨╜╨╛╤Б╤В╤М ╨▓ ╤А╨╡╤И╨░╤О╤Й╨╕╨╡ ╨╝╨╛╨╝╨╡╨╜╤В╤Л
        },
        'ambition': {
            'shot_attempts': 0.08,   # +8% ╤З╨░╤Б╤В╨╛╤В╨░ ╤Г╨┤╨░╤А╨╛╨▓
            'forward_runs': 0.10,    # +10% ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨░╤В╨░╨║╤Г╤О╤Й╨╕╨╝ ╨┐╨╡╤А╨╡╨▒╨╡╨╢╨║╨░╨╝
            'risk_in_attack': 0.06,  # +6% ╤А╨╕╤Б╨║ ╨▓ ╨░╤В╨░╨║╨╡
        },
        'charisma': {
            'referee_influence': 0.03, # +3% ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╨╜╨░ ╤Б╤Г╨┤╨╡╨╣╤Б╨║╨╕╨╡ ╤А╨╡╤И╨╡╨╜╨╕╤П
            'opponent_pressure': 0.05, # +5% ╨┐╤Б╨╕╤Е╨╛╨╗╨╛╨│╨╕╤З╨╡╤Б╨║╨╛╨╡ ╨┤╨░╨▓╨╗╨╡╨╜╨╕╨╡ ╨╜╨░ ╨┐╤А╨╛╤В╨╕╨▓╨╜╨╕╨║╨░
        },
        'endurance': {
            'late_game_performance': 0.12, # +12% ╤Н╤Д╤Д╨╡╨║╤В╨╕╨▓╨╜╨╛╤Б╤В╤М ╨▓ ╨║╨╛╨╜╤Ж╨╡ ╨╝╨░╤В╤З╨░
            'stamina_recovery': 0.08,       # +8% ╨▓╨╛╤Б╤Б╤В╨░╨╜╨╛╨▓╨╗╨╡╨╜╨╕╨╡ ╨▓╤Л╨╜╨╛╤Б╨╗╨╕╨▓╨╛╤Б╤В╨╕
        },
        'adaptability': {
            'tactical_changes': 0.08,  # +8% ╨░╨┤╨░╨┐╤В╨░╤Ж╨╕╤П ╨║ ╤В╨░╨║╤В╨╕╤З╨╡╤Б╨║╨╕╨╝ ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╤П╨╝
            'weather_conditions': 0.06, # +6% ╨░╨┤╨░╨┐╤В╨░╤Ж╨╕╤П ╨║ ╨┐╨╛╨│╨╛╨┤╨╜╤Л╨╝ ╤Г╤Б╨╗╨╛╨▓╨╕╤П╨╝
        }
    }
    
    @staticmethod
    def _is_personality_enabled():
        """╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╤В, ╨▓╨║╨╗╤О╤З╨╡╨╜ ╨╗╨╕ personality engine ╨▓ ╨╜╨░╤Б╤В╤А╨╛╨╣╨║╨░╤Е."""
        return getattr(settings, 'USE_PERSONALITY_ENGINE', False)
    
    @staticmethod
    def _normalize_trait_value(trait_value):
        """
        ╨Э╨╛╤А╨╝╨░╨╗╨╕╨╖╤Г╨╡╤В ╨╖╨╜╨░╤З╨╡╨╜╨╕╨╡ trait (1-20) ╨▓ ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А (-0.25 to +0.25).
        
        Args:
            trait_value (int): ╨Ч╨╜╨░╤З╨╡╨╜╨╕╨╡ trait ╨╛╤В 1 ╨┤╨╛ 20
            
        Returns:
            float: ╨Э╨╛╤А╨╝╨░╨╗╨╕╨╖╨╛╨▓╨░╨╜╨╜╤Л╨╣ ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А
        """
        if trait_value is None:
            return 0.0
        
        # ╨Я╤А╨╡╨╛╨▒╤А╨░╨╖╤Г╨╡╨╝ ╨┤╨╕╨░╨┐╨░╨╖╨╛╨╜ 1-20 ╨▓ -0.25 to +0.25
        # 10.5 - ╤Б╤А╨╡╨┤╨╜╤П╤П ╤В╨╛╤З╨║╨░, 1 -> -0.25, 20 -> +0.25
        normalized = (trait_value - 10.5) / 38.0  # 38 = (20-1) * 2
        return max(-0.25, min(0.25, normalized))
    
    @staticmethod
    def _get_trait_value(player, trait_name):
        """
        ╨Я╨╛╨╗╤Г╤З╨░╨╡╤В ╨╖╨╜╨░╤З╨╡╨╜╨╕╨╡ ╤Г╨║╨░╨╖╨░╨╜╨╜╨╛╨│╨╛ personality trait ╨╕╨│╤А╨╛╨║╨░.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            trait_name (str): ╨Э╨░╨╖╨▓╨░╨╜╨╕╨╡ trait
            
        Returns:
            int: ╨Ч╨╜╨░╤З╨╡╨╜╨╕╨╡ trait ╨╕╨╗╨╕ None ╨╡╤Б╨╗╨╕ ╨╜╨╡ ╨╜╨░╨╣╨┤╨╡╨╜╨╛
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
        ╨Т╤Л╤З╨╕╤Б╨╗╤П╨╡╤В ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╨╕ ╨║ ╤Д╨╛╨╗╨░╨╝ ╨┤╨╗╤П ╨╕╨│╤А╨╛╨║╨░.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            
        Returns:
            float: ╨Ь╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤Д╨╛╨╗╨╛╨▓ (-0.25 to +0.25)
        """
        if not PersonalityModifier._is_personality_enabled():
            return 0.0
        
        try:
            # ╨Р╨│╤А╨╡╤Б╤Б╨╕╨▓╨╜╨╛╤Б╤В╤М ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤Д╨╛╨╗╨░╨╝
            aggression = PersonalityModifier._get_trait_value(player, 'aggression')
            aggression_modifier = PersonalityModifier._normalize_trait_value(aggression)
            aggression_influence = aggression_modifier * PersonalityModifier.TRAIT_INFLUENCES['aggression']['fouls']
            
            # ╨в╨╡╤А╨┐╨╡╨╗╨╕╨▓╨╛╤Б╤В╤М ╤Б╨╜╨╕╨╢╨░╨╡╤В ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤Д╨╛╨╗╨░╨╝
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
        ╨Т╤Л╤З╨╕╤Б╨╗╤П╨╡╤В ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤В╨╛╤З╨╜╨╛╤Б╤В╨╕ ╨╕ ╨┐╤А╨╡╨┤╨┐╨╛╤З╤В╨╡╨╜╨╕╤П ╨┐╨░╤Б╨╛╨▓ ╨┤╨╗╤П ╨╕╨│╤А╨╛╨║╨░.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            context (dict, optional): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕
                - 'pass_type': 'short', 'long', 'through'
                - 'pressure': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤П (0.0-1.0)
                - 'time_pressure': ╨▓╤А╨╡╨╝╨╡╨╜╨╜╨╛╨╡ ╨┤╨░╨▓╨╗╨╡╨╜╨╕╨╡ (0.0-1.0)
            
        Returns:
            dict: ╨Ь╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л ╨┐╨░╤Б╨╛╨▓
                - 'accuracy': ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤В╨╛╤З╨╜╨╛╤Б╤В╨╕
                - 'preference': ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╨┐╤А╨╡╨┤╨┐╨╛╤З╤В╨╡╨╜╨╕╤П ╨┐╨░╤Б╨░
                - 'risk': ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤А╨╕╤Б╨║╨╛╨▓╨░╨╜╨╜╨╛╤Б╤В╨╕ ╨┐╨░╤Б╨░
        """
        if not PersonalityModifier._is_personality_enabled():
            return {'accuracy': 0.0, 'preference': 0.0, 'risk': 0.0}
        
        try:
            context = context or {}
            pass_type = context.get('pass_type', 'short')
            
            # ╨С╨░╨╖╨╛╨▓╤Л╨╡ ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л
            result = {'accuracy': 0.0, 'preference': 0.0, 'risk': 0.0}
            
            # ╨в╨╡╤А╨┐╨╡╨╗╨╕╨▓╨╛╤Б╤В╤М ╤Г╨╗╤Г╤З╤И╨░╨╡╤В ╤В╨╛╤З╨╜╨╛╤Б╤В╤М ╨┐╨░╤Б╨╛╨▓
            patience = PersonalityModifier._get_trait_value(player, 'patience')
            if patience:
                patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                result['accuracy'] += patience_modifier * PersonalityModifier.TRAIT_INFLUENCES['patience']['pass_accuracy']
            
            # ╨Ъ╨╛╨╝╨░╨╜╨┤╨╜╨░╤П ╨╕╨│╤А╨░ ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╨┐╤А╨╡╨┤╨┐╨╛╤З╤В╨╡╨╜╨╕╨╡ ╨┐╨░╤Б╨░
            teamwork = PersonalityModifier._get_trait_value(player, 'teamwork')
            if teamwork:
                teamwork_modifier = PersonalityModifier._normalize_trait_value(teamwork)
                result['preference'] += teamwork_modifier * PersonalityModifier.TRAIT_INFLUENCES['teamwork']['pass_preference']
            
            # ╨б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤А╨╕╤Б╨║╤Г ╨▓╨╗╨╕╤П╨╡╤В ╨╜╨░ ╨▓╤Л╨▒╨╛╤А ╤В╨╕╨┐╨░ ╨┐╨░╤Б╨░
            risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
            if risk_taking:
                risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                
                if pass_type == 'long':
                    result['preference'] += risk_modifier * PersonalityModifier.TRAIT_INFLUENCES['risk_taking']['long_passes']
                elif pass_type == 'through':
                    result['preference'] += risk_modifier * PersonalityModifier.TRAIT_INFLUENCES['risk_taking']['through_balls']
                
                result['risk'] += risk_modifier
            
            # ╨Ю╨│╤А╨░╨╜╨╕╤З╨╕╨▓╨░╨╡╨╝ ╨╖╨╜╨░╤З╨╡╨╜╨╕╤П
            for key in result:
                result[key] = max(-0.25, min(0.25, result[key]))
            
            return result
            
        except Exception as e:
            logger.warning(f"Error calculating pass modifier for player {player.id}: {e}")
            return {'accuracy': 0.0, 'preference': 0.0, 'risk': 0.0}
    
    @staticmethod
    def get_shot_modifier(player, context=None):
        """
        ╨Т╤Л╤З╨╕╤Б╨╗╤П╨╡╤В ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤Г╨┤╨░╤А╨╛╨▓ ╨┤╨╗╤П ╨╕╨│╤А╨╛╨║╨░.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            context (dict, optional): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕
                - 'shot_type': 'close', 'long', 'penalty'
                - 'pressure': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤П (0.0-1.0)
                - 'match_minute': ╨╝╨╕╨╜╤Г╤В╨░ ╨╝╨░╤В╤З╨░
                - 'score_difference': ╤А╨░╨╖╨╜╨╛╤Б╤В╤М ╨▓ ╤Б╤З╨╡╤В╨╡
            
        Returns:
            dict: ╨Ь╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л ╤Г╨┤╨░╤А╨╛╨▓
                - 'accuracy': ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤В╨╛╤З╨╜╨╛╤Б╤В╨╕
                - 'frequency': ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤З╨░╤Б╤В╨╛╤В╤Л ╤Г╨┤╨░╤А╨╛╨▓
                - 'power': ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤Б╨╕╨╗╤Л ╤Г╨┤╨░╤А╨░
        """
        if not PersonalityModifier._is_personality_enabled():
            return {'accuracy': 0.0, 'frequency': 0.0, 'power': 0.0}
        
        try:
            context = context or {}
            shot_type = context.get('shot_type', 'close')
            match_minute = context.get('match_minute', 45)
            
            result = {'accuracy': 0.0, 'frequency': 0.0, 'power': 0.0}
            
            # ╨г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М ╤Г╨╗╤Г╤З╤И╨░╨╡╤В ╤В╨╛╤З╨╜╨╛╤Б╤В╤М ╤Г╨┤╨░╤А╨╛╨▓
            confidence = PersonalityModifier._get_trait_value(player, 'confidence')
            if confidence:
                confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
                result['accuracy'] += confidence_modifier * PersonalityModifier.TRAIT_INFLUENCES['confidence']['shot_accuracy']
                
                # ╨Ю╤Б╨╛╨▒╨╡╨╜╨╜╨╛ ╨▓╨░╨╢╨╜╨╛ ╨┤╨╗╤П ╨┐╨╡╨╜╨░╨╗╤М╤В╨╕
                if shot_type == 'penalty':
                    result['accuracy'] += confidence_modifier * PersonalityModifier.TRAIT_INFLUENCES['confidence']['penalties']
            
            # ╨Р╨╝╨▒╨╕╤Ж╨╕╨╛╨╖╨╜╨╛╤Б╤В╤М ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤З╨░╤Б╤В╨╛╤В╤Г ╤Г╨┤╨░╤А╨╛╨▓
            ambition = PersonalityModifier._get_trait_value(player, 'ambition')
            if ambition:
                ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
                result['frequency'] += ambition_modifier * PersonalityModifier.TRAIT_INFLUENCES['ambition']['shot_attempts']
            
            # ╨б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤А╨╕╤Б╨║╤Г ╨┤╨╗╤П ╨┤╨░╨╗╤М╨╜╨╕╤Е ╤Г╨┤╨░╤А╨╛╨▓
            risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
            if risk_taking and shot_type == 'long':
                risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                result['frequency'] += risk_modifier * PersonalityModifier.TRAIT_INFLUENCES['risk_taking']['long_shots']
            
            # ╨Т╤Л╨╜╨╛╤Б╨╗╨╕╨▓╨╛╤Б╤В╤М ╨▓╨╗╨╕╤П╨╡╤В ╨╜╨░ ╤В╨╛╤З╨╜╨╛╤Б╤В╤М ╨▓ ╨║╨╛╨╜╤Ж╨╡ ╨╝╨░╤В╤З╨░
            endurance = PersonalityModifier._get_trait_value(player, 'endurance')
            if endurance and match_minute > 75:
                endurance_modifier = PersonalityModifier._normalize_trait_value(endurance)
                late_game_bonus = endurance_modifier * PersonalityModifier.TRAIT_INFLUENCES['endurance']['late_game_performance']
                result['accuracy'] += late_game_bonus
                result['power'] += late_game_bonus * 0.5  # ╨Я╨╛╨╗╨╛╨▓╨╕╨╜╨╜╨╛╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╨╜╨░ ╤Б╨╕╨╗╤Г
            
            # ╨Ю╨│╤А╨░╨╜╨╕╤З╨╕╨▓╨░╨╡╨╝ ╨╖╨╜╨░╤З╨╡╨╜╨╕╤П
            for key in result:
                result[key] = max(-0.25, min(0.25, result[key]))
            
            return result
            
        except Exception as e:
            logger.warning(f"Error calculating shot modifier for player {player.id}: {e}")
            return {'accuracy': 0.0, 'frequency': 0.0, 'power': 0.0}
    
    @staticmethod
    def get_decision_modifier(player, action_type, context=None):
        """
        ╨Т╤Л╤З╨╕╤Б╨╗╤П╨╡╤В ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╨▓╤Л╨▒╨╛╤А╨░ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╣ ╨┤╨╗╤П ╨╕╨│╤А╨╛╨║╨░.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            action_type (str): ╨в╨╕╨┐ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П ('pass', 'shoot', 'dribble', 'tackle')
            context (dict, optional): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕
                - 'teammates_nearby': ╨║╨╛╨╗╨╕╤З╨╡╤Б╤В╨▓╨╛ ╨┐╨░╤А╤В╨╜╨╡╤А╨╛╨▓ ╤А╤П╨┤╨╛╨╝
                - 'opponents_nearby': ╨║╨╛╨╗╨╕╤З╨╡╤Б╤В╨▓╨╛ ╨┐╤А╨╛╤В╨╕╨▓╨╜╨╕╨║╨╛╨▓ ╤А╤П╨┤╨╛╨╝
                - 'goal_distance': ╤А╨░╤Б╤Б╤В╨╛╤П╨╜╨╕╨╡ ╨┤╨╛ ╨▓╨╛╤А╨╛╤В
                - 'match_situation': 'winning', 'losing', 'drawing'
            
        Returns:
            float: ╨Ь╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╨╕ ╨║ ╨▓╤Л╨▒╨╛╤А╤Г ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П (-0.25 to +0.25)
        """
        if not PersonalityModifier._is_personality_enabled():
            return 0.0
        
        try:
            context = context or {}
            modifier = 0.0
            
            if action_type == 'pass':
                # ╨Ъ╨╛╨╝╨░╨╜╨┤╨╜╨░╤П ╨╕╨│╤А╨░ ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨┐╨░╤Б╤Г
                teamwork = PersonalityModifier._get_trait_value(player, 'teamwork')
                if teamwork:
                    teamwork_modifier = PersonalityModifier._normalize_trait_value(teamwork)
                    modifier += teamwork_modifier * PersonalityModifier.TRAIT_INFLUENCES['teamwork']['pass_preference']
                
                # ╨в╨╡╤А╨┐╨╡╨╗╨╕╨▓╨╛╤Б╤В╤М ╤В╨╛╨╢╨╡ ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨┐╨░╤Б╤Г
                patience = PersonalityModifier._get_trait_value(player, 'patience')
                if patience:
                    patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                    modifier += patience_modifier * 0.08  # ╨Ф╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╨╛╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╤В╨╡╤А╨┐╨╡╨╗╨╕╨▓╨╛╤Б╤В╨╕
            
            elif action_type == 'shoot':
                # ╨Р╨╝╨▒╨╕╤Ж╨╕╨╛╨╖╨╜╨╛╤Б╤В╤М ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤Г╨┤╨░╤А╨░╨╝
                ambition = PersonalityModifier._get_trait_value(player, 'ambition')
                if ambition:
                    ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
                    modifier += ambition_modifier * PersonalityModifier.TRAIT_INFLUENCES['ambition']['shot_attempts']
                
                # ╨г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М ╤В╨╛╨╢╨╡ ╨▓╨╗╨╕╤П╨╡╤В ╨╜╨░ ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤Г╨┤╨░╤А╨░╨╝
                confidence = PersonalityModifier._get_trait_value(player, 'confidence')
                if confidence:
                    confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
                    modifier += confidence_modifier * 0.06  # ╨Ь╨╡╨╜╤М╤И╨╡╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╤З╨╡╨╝ ╨░╨╝╨▒╨╕╤Ж╨╕╨╕
            
            elif action_type == 'dribble':
                # ╨б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤А╨╕╤Б╨║╤Г ╨╕ ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╤О╤В ╨┤╤А╨╕╨▒╨╗╨╕╨╜╨│
                risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
                if risk_taking:
                    risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                    modifier += risk_modifier * PersonalityModifier.TRAIT_INFLUENCES['risk_taking']['solo_runs']
                
                confidence = PersonalityModifier._get_trait_value(player, 'confidence')
                if confidence:
                    confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
                    modifier += confidence_modifier * PersonalityModifier.TRAIT_INFLUENCES['confidence']['dribbling']
            
            elif action_type == 'tackle':
                # ╨Р╨│╤А╨╡╤Б╤Б╨╕╨▓╨╜╨╛╤Б╤В╤М ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨╛╤В╨▒╨╛╤А╨░╨╝
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
        ╨Т╤Л╤З╨╕╤Б╨╗╤П╨╡╤В ╨▓╨╗╨╕╤П╨╜╨╕╨╡ personality traits ╨╜╨░ ╨╝╨╛╤А╨░╨╗╤М ╨╕╨│╤А╨╛╨║╨░ ╨╕ ╨║╨╛╨╝╨░╨╜╨┤╤Л.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            team_performance (dict, optional): ╨Я╨╛╨║╨░╨╖╨░╤В╨╡╨╗╨╕ ╨║╨╛╨╝╨░╨╜╨┤╤Л
                - 'recent_results': ╤Б╨┐╨╕╤Б╨╛╨║ ╨┐╨╛╤Б╨╗╨╡╨┤╨╜╨╕╤Е ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В╨╛╨▓
                - 'current_score': ╤В╨╡╨║╤Г╤Й╨╕╨╣ ╤Б╤З╨╡╤В
                - 'match_events': ╨▓╨░╨╢╨╜╤Л╨╡ ╤Б╨╛╨▒╤Л╤В╨╕╤П ╨╝╨░╤В╤З╨░
            
        Returns:
            dict: ╨Т╨╗╨╕╤П╨╜╨╕╨╡ ╨╜╨░ ╨╝╨╛╤А╨░╨╗╤М
                - 'self_morale': ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╨╜╨░ ╤Б╨╛╨▒╤Б╤В╨▓╨╡╨╜╨╜╤Г╤О ╨╝╨╛╤А╨░╨╗╤М
                - 'team_morale': ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╨╜╨░ ╨╝╨╛╤А╨░╨╗╤М ╨║╨╛╨╝╨░╨╜╨┤╤Л
        """
        if not PersonalityModifier._is_personality_enabled():
            return {'self_morale': 0.0, 'team_morale': 0.0}
        
        try:
            result = {'self_morale': 0.0, 'team_morale': 0.0}
            
            # ╨Ы╨╕╨┤╨╡╤А╤Б╤В╨▓╨╛ ╨▓╨╗╨╕╤П╨╡╤В ╨╜╨░ ╨╝╨╛╤А╨░╨╗╤М ╨║╨╛╨╝╨░╨╜╨┤╤Л
            leadership = PersonalityModifier._get_trait_value(player, 'leadership')
            if leadership:
                leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
                result['team_morale'] += leadership_modifier * PersonalityModifier.TRAIT_INFLUENCES['leadership']['team_morale']
            
            # ╨е╨░╤А╨╕╨╖╨╝╨░ ╤В╨╛╨╢╨╡ ╨▓╨╗╨╕╤П╨╡╤В ╨╜╨░ ╨║╨╛╨╝╨░╨╜╨┤╤Г
            charisma = PersonalityModifier._get_trait_value(player, 'charisma')
            if charisma:
                charisma_modifier = PersonalityModifier._normalize_trait_value(charisma)
                result['team_morale'] += charisma_modifier * 0.03  # ╨Ф╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╨╛╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╤Е╨░╤А╨╕╨╖╨╝╤Л
            
            # ╨г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М ╨▓╨╗╨╕╤П╨╡╤В ╨╜╨░ ╤Б╨╛╨▒╤Б╤В╨▓╨╡╨╜╨╜╤Г╤О ╨╝╨╛╤А╨░╨╗╤М
            confidence = PersonalityModifier._get_trait_value(player, 'confidence')
            if confidence:
                confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
                result['self_morale'] += confidence_modifier * 0.08
            
            # ╨Ю╨│╤А╨░╨╜╨╕╤З╨╕╨▓╨░╨╡╨╝ ╨╖╨╜╨░╤З╨╡╨╜╨╕╤П
            for key in result:
                result[key] = max(-0.15, min(0.15, result[key]))  # ╨Ь╨╡╨╜╤М╤И╨╕╨╣ ╨┤╨╕╨░╨┐╨░╨╖╨╛╨╜ ╨┤╨╗╤П ╨╝╨╛╤А╨░╨╗╨╕
            
            return result
            
        except Exception as e:
            logger.warning(f"Error calculating morale influence for player {player.id}: {e}")
            return {'self_morale': 0.0, 'team_morale': 0.0}
    
    @staticmethod
    def get_adaptation_modifier(player, situation_context):
        """
        ╨Т╤Л╤З╨╕╤Б╨╗╤П╨╡╤В ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╨░╨┤╨░╨┐╤В╨░╤Ж╨╕╨╕ ╨║ ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╤П╨╝ ╨▓ ╨╕╨│╤А╨╡.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            situation_context (dict): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╨╣
                - 'tactical_change': ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╨╡ ╤В╨░╨║╤В╨╕╨║╨╕
                - 'weather_change': ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╨╡ ╨┐╨╛╨│╨╛╨┤╤Л
                - 'opponent_strategy': ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╨╡ ╤Б╤В╤А╨░╤В╨╡╨│╨╕╨╕ ╨┐╤А╨╛╤В╨╕╨▓╨╜╨╕╨║╨░
                - 'match_phase': ╤Д╨░╨╖╨░ ╨╝╨░╤В╤З╨░
            
        Returns:
            float: ╨Ь╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А ╨░╨┤╨░╨┐╤В╨░╤Ж╨╕╨╕ (-0.15 to +0.15)
        """
        if not PersonalityModifier._is_personality_enabled():
            return 0.0
        
        try:
            modifier = 0.0
            
            # ╨Р╨┤╨░╨┐╤В╨╕╨▓╨╜╨╛╤Б╤В╤М - ╨╛╤Б╨╜╨╛╨▓╨╜╨╛╨╣ ╤Д╨░╨║╤В╨╛╤А
            adaptability = PersonalityModifier._get_trait_value(player, 'adaptability')
            if adaptability:
                adaptability_modifier = PersonalityModifier._normalize_trait_value(adaptability)
                
                if 'tactical_change' in situation_context:
                    modifier += adaptability_modifier * PersonalityModifier.TRAIT_INFLUENCES['adaptability']['tactical_changes']
                
                if 'weather_change' in situation_context:
                    modifier += adaptability_modifier * PersonalityModifier.TRAIT_INFLUENCES['adaptability']['weather_conditions']
            
            # ╨Ы╨╕╨┤╨╡╤А╤Б╤В╨▓╨╛ ╨┐╨╛╨╝╨╛╨│╨░╨╡╤В ╨▓ ╨░╨┤╨░╨┐╤В╨░╤Ж╨╕╨╕
            leadership = PersonalityModifier._get_trait_value(player, 'leadership')
            if leadership:
                leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
                modifier += leadership_modifier * 0.04  # ╨Ф╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╨╛╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡ ╨╗╨╕╨┤╨╡╤А╤Б╤В╨▓╨░
            
            return max(-0.15, min(0.15, modifier))
            
        except Exception as e:
            logger.warning(f"Error calculating adaptation modifier for player {player.id}: {e}")
            return 0.0


class PersonalityDecisionEngine:
    """
    ╨Ф╨▓╨╕╨╢╨╛╨║ ╨┐╤А╨╕╨╜╤П╤В╨╕╤П ╤А╨╡╤И╨╡╨╜╨╕╨╣ ╨╕╨│╤А╨╛╨║╨╛╨▓ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ personality traits.
    
    ╨Ю╨▒╨╡╤Б╨┐╨╡╤З╨╕╨▓╨░╨╡╤В ╨║╨╛╨╜╤В╨╡╨║╤Б╤В╨╜╨╛-╨╖╨░╨▓╨╕╤Б╨╕╨╝╨╛╨╡ ╨┐╤А╨╕╨╜╤П╤В╨╕╨╡ ╤А╨╡╤И╨╡╨╜╨╕╨╣ ╨╕╨│╤А╨╛╨║╨░╨╝╨╕,
    ╤Г╤З╨╕╤В╤Л╨▓╨░╤П ╨╕╤Е ╨╗╨╕╤З╨╜╨╛╤Б╤В╨╜╤Л╨╡ ╤Е╨░╤А╨░╨║╤В╨╡╤А╨╕╤Б╤В╨╕╨║╨╕, ╨╕╨│╤А╨╛╨▓╤Г╤О ╤Б╨╕╤В╤Г╨░╤Ж╨╕╤О ╨╕ ╤Б╤В╤А╨╡╤Б╤Б.
    
    ╨Ъ╨╛╨╜╤Д╨╕╨│╤Г╤А╨░╤Ж╨╕╤П: 40% ╤А╨╡╨░╨╗╨╕╨╖╨╝, 60% ╨│╨╡╨╣╨╝╨┐╨╗╨╡╨╣
    - ╨а╨╡╤И╨╡╨╜╨╕╤П ╨▓╨╗╨╕╤П╤О╤В ╨╜╨░ ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╨┐╤А╨╛╤Ж╨╡╤Б╤Б, ╨╜╨╛ ╨╛╤Б╤В╨░╤О╤В╤Б╤П ╤Б╨▒╨░╨╗╨░╨╜╤Б╨╕╤А╨╛╨▓╨░╨╜╨╜╤Л╨╝╨╕
    - ╨Ь╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л ╨╜╨░╨║╨╗╨░╨┤╤Л╨▓╨░╤О╤В╤Б╤П ╨╜╨░ ╨▒╨░╨╖╨╛╨▓╤Г╤О ╨╗╨╛╨│╨╕╨║╤Г ╨┐╤А╨╕╨╜╤П╤В╨╕╤П ╤А╨╡╤И╨╡╨╜╨╕╨╣
    """
    
    # ╨С╨░╨╖╨╛╨▓╤Л╨╡ ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╨╕ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╣ (╨▒╨╡╨╖ personality ╨▓╨╗╨╕╤П╨╜╨╕╨╣)
    BASE_ACTION_PROBABILITIES = {
        'pass': 0.40,       # ╨С╨░╨╖╨╛╨▓╨░╤П ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨┐╨░╤Б╤Г
        'shoot': 0.15,      # ╨С╨░╨╖╨╛╨▓╨░╤П ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤Г╨┤╨░╤А╤Г
        'dribble': 0.20,    # ╨С╨░╨╖╨╛╨▓╨░╤П ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨┤╤А╨╕╨▒╨╗╨╕╨╜╨│╤Г
        'tackle': 0.25,     # ╨С╨░╨╖╨╛╨▓╨░╤П ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╨╛╤В╨▒╨╛╤А╤Г (╨┤╨╗╤П ╨╖╨░╤Й╨╕╤В╤Л)
    }
    
    # ╨Я╨╛╤А╨╛╨│╨╕ ╨┤╨╗╤П ╤А╨░╨╖╨╗╨╕╤З╨╜╤Л╤Е ╤А╨╡╤И╨╡╨╜╨╕╨╣
    DECISION_THRESHOLDS = {
        'risky_action': 0.60,       # ╨Я╨╛╤А╨╛╨│ ╨┤╨╗╤П ╤А╨╕╤Б╨║╨╛╨▓╨░╨╜╨╜╤Л╤Е ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╣
        'shot_timing': 0.50,        # ╨Я╨╛╤А╨╛╨│ ╨┤╨╗╤П ╨▓╤А╨╡╨╝╨╡╨╜╨╕ ╤Г╨┤╨░╤А╨░
        'pass_confidence': 0.40,    # ╨Ь╨╕╨╜╨╕╨╝╨░╨╗╤М╨╜╨░╤П ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М ╨┤╨╗╤П ╨┐╨░╤Б╨░
        'pressure_resistance': 0.70, # ╨Я╨╛╤А╨╛╨│ ╤Г╤Б╤В╨╛╨╣╤З╨╕╨▓╨╛╤Б╤В╨╕ ╨║ ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤О
    }
    
    @staticmethod
    def choose_action_type(player, context=None):
        """
        ╨Т╤Л╨▒╨╕╤А╨░╨╡╤В ╤В╨╕╨┐ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П ╨┤╨╗╤П ╨╕╨│╤А╨╛╨║╨░ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ personality traits ╨╕ ╨║╨╛╨╜╤В╨╡╨║╤Б╤В╨░.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            context (dict, optional): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕
                - 'position': ╨┐╨╛╨╖╨╕╤Ж╨╕╤П ╨╜╨░ ╨┐╨╛╨╗╨╡ (x, y)
                - 'teammates_nearby': ╨║╨╛╨╗╨╕╤З╨╡╤Б╤В╨▓╨╛ ╨┐╨░╤А╤В╨╜╨╡╤А╨╛╨▓ ╤А╤П╨┤╨╛╨╝
                - 'opponents_nearby': ╨║╨╛╨╗╨╕╤З╨╡╤Б╤В╨▓╨╛ ╨┐╤А╨╛╤В╨╕╨▓╨╜╨╕╨║╨╛╨▓ ╤А╤П╨┤╨╛╨╝
                - 'goal_distance': ╤А╨░╤Б╤Б╤В╨╛╤П╨╜╨╕╨╡ ╨┤╨╛ ╨▓╨╛╤А╨╛╤В
                - 'match_minute': ╨╝╨╕╨╜╤Г╤В╨░ ╨╝╨░╤В╤З╨░
                - 'score_difference': ╤А╨░╨╖╨╜╨╛╤Б╤В╤М ╨▓ ╤Б╤З╨╡╤В╨╡
                - 'possession_type': 'attack', 'midfield', 'defense'
                - 'pressure_level': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤П (0.0-1.0)
            
        Returns:
            str: ╨Т╤Л╨▒╤А╨░╨╜╨╜╨╛╨╡ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╡ ('pass', 'shoot', 'dribble', 'tackle')
        
        Examples:
            >>> context = {
            ...     'goal_distance': 20,
            ...     'teammates_nearby': 2,
            ...     'opponents_nearby': 1,
            ...     'possession_type': 'attack'
            ... }
            >>> action = PersonalityDecisionEngine.choose_action_type(player, context)
            >>> print(action)  # 'shoot' ╨╕╨╗╨╕ 'pass' ╨▓ ╨╖╨░╨▓╨╕╤Б╨╕╨╝╨╛╤Б╤В╨╕ ╨╛╤В personality
        """
        context = context or {}
        
        # ╨С╨░╨╖╨╛╨▓╤Л╨╡ ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╨╕
        probabilities = PersonalityDecisionEngine.BASE_ACTION_PROBABILITIES.copy()
        
        # ╨Ъ╨╛╤А╤А╨╡╨║╤В╨╕╤А╨╛╨▓╨║╨░ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ ╨┐╨╛╨╖╨╕╤Ж╨╕╨╕
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
        
        # ╨Я╤А╨╕╨╝╨╡╨╜╤П╨╡╨╝ personality ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л
        for action in probabilities:
            personality_modifier = PersonalityModifier.get_decision_modifier(player, action, context)
            probabilities[action] += personality_modifier
        
        # ╨Ъ╨╛╤А╤А╨╡╨║╤В╨╕╤А╨╛╨▓╨║╨░ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ ╨║╨╛╨╜╤В╨╡╨║╤Б╤В╨░
        goal_distance = context.get('goal_distance', 50)
        teammates_nearby = context.get('teammates_nearby', 1)
        opponents_nearby = context.get('opponents_nearby', 1)
        
        # ╨С╨╗╨╕╨╖╨╛╤Б╤В╤М ╨║ ╨▓╨╛╤А╨╛╤В╨░╨╝ ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤Г╨┤╨░╤А╤Г
        if goal_distance < 25:
            probabilities['shoot'] += 0.20
        elif goal_distance < 40:
            probabilities['shoot'] += 0.10
        
        # ╨Ь╨╜╨╛╨│╨╛ ╨┐╨░╤А╤В╨╜╨╡╤А╨╛╨▓ ╤А╤П╨┤╨╛╨╝ - ╨▒╨╛╨╗╤М╤И╨╡ ╨┐╨░╤Б╨╛╨▓
        if teammates_nearby >= 3:
            probabilities['pass'] += 0.15
        
        # ╨Ь╨╜╨╛╨│╨╛ ╨┐╤А╨╛╤В╨╕╨▓╨╜╨╕╨║╨╛╨▓ - ╨╝╨╡╨╜╤М╤И╨╡ ╨┤╤А╨╕╨▒╨╗╨╕╨╜╨│╨░
        if opponents_nearby >= 2:
            probabilities['dribble'] -= 0.15
            probabilities['tackle'] += 0.10
        
        # ╨Э╨╛╤А╨╝╨░╨╗╨╕╨╖╤Г╨╡╨╝ ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╨╕
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: max(0.0, v/total) for k, v in probabilities.items()}
        
        # ╨Т╤Л╨▒╨╕╤А╨░╨╡╨╝ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╡ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╨╡╨╣
        rand_value = random.random()
        cumulative = 0.0
        
        for action, probability in probabilities.items():
            cumulative += probability
            if rand_value <= cumulative:
                return action
        
        # Fallback - ╨▓╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╨╝ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╡ ╤Б ╨╜╨░╨╕╨▒╨╛╨╗╤М╤И╨╡╨╣ ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╤М╤О
        return max(probabilities, key=probabilities.get)
    
    @staticmethod
    def should_attempt_risky_action(player, risk_level, context=None):
        """
        ╨Ю╨┐╤А╨╡╨┤╨╡╨╗╤П╨╡╤В, ╨┤╨╛╨╗╨╢╨╡╨╜ ╨╗╨╕ ╨╕╨│╤А╨╛╨║ ╨┐╤А╨╡╨┤╨┐╤А╨╕╨╜╤П╤В╤М ╤А╨╕╤Б╨║╨╛╨▓╨░╨╜╨╜╨╛╨╡ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╡.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            risk_level (float): ╨г╤А╨╛╨▓╨╡╨╜╤М ╤А╨╕╤Б╨║╨░ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П (0.0-1.0)
            context (dict, optional): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕
                - 'match_minute': ╨╝╨╕╨╜╤Г╤В╨░ ╨╝╨░╤В╤З╨░
                - 'score_difference': ╤А╨░╨╖╨╜╨╛╤Б╤В╤М ╨▓ ╤Б╤З╨╡╤В╨╡
                - 'pressure_level': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤П
                - 'team_situation': 'winning', 'losing', 'drawing'
                - 'importance': ╨▓╨░╨╢╨╜╨╛╤Б╤В╤М ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕ (0.0-1.0)
            
        Returns:
            bool: True ╨╡╤Б╨╗╨╕ ╤Б╤В╨╛╨╕╤В ╤А╨╕╤Б╨║╨╛╨▓╨░╤В╤М, False ╨╡╤Б╨╗╨╕ ╨╜╨╡╤В
        
        Examples:
            >>> context = {
            ...     'score_difference': -1,  # ╨Я╤А╨╛╨╕╨│╤А╤Л╨▓╨░╨╡╨╝
            ...     'match_minute': 85,      # ╨Ъ╨╛╨╜╨╡╤Ж ╨╝╨░╤В╤З╨░
            ...     'importance': 0.9        # ╨Т╨░╨╢╨╜╨░╤П ╤Б╨╕╤В╤Г╨░╤Ж╨╕╤П
            ... }
            >>> should_risk = PersonalityDecisionEngine.should_attempt_risky_action(
            ...     player, 0.7, context
            ... )
            >>> print(should_risk)  # True ╨╡╤Б╨╗╨╕ ╨╕╨│╤А╨╛╨║ ╤Б╨║╨╗╨╛╨╜╨╡╨╜ ╨║ ╤А╨╕╤Б╨║╤Г
        """
        context = context or {}
        
        # ╨С╨░╨╖╨╛╨▓╤Л╨╣ ╨┐╨╛╤А╨╛╨│ ╤А╨╕╤Б╨║╨░
        base_threshold = PersonalityDecisionEngine.DECISION_THRESHOLDS['risky_action']
        
        # ╨Я╨╛╨╗╤Г╤З╨░╨╡╨╝ personality ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л
        risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
        confidence = PersonalityModifier._get_trait_value(player, 'confidence')
        patience = PersonalityModifier._get_trait_value(player, 'patience')
        
        # ╨а╨░╤Б╤Б╤З╨╕╤В╤Л╨▓╨░╨╡╨╝ ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤А╨╕╤Б╨║╤Г
        risk_tendency = 0.5  # ╨Э╨╡╨╣╤В╤А╨░╨╗╤М╨╜╨░╤П ╨▒╨░╨╖╨╛╨▓╨░╤П ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М
        
        if risk_taking:
            risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
            risk_tendency += risk_modifier * 0.4  # ╨б╨╕╨╗╤М╨╜╨╛╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡
        
        if confidence:
            confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
            risk_tendency += confidence_modifier * 0.2  # ╨г╨╝╨╡╤А╨╡╨╜╨╜╨╛╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡
        
        if patience:
            patience_modifier = PersonalityModifier._normalize_trait_value(patience)
            risk_tendency -= patience_modifier * 0.3  # ╨б╨╜╨╕╨╢╨░╨╡╤В ╤Б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤А╨╕╤Б╨║╤Г
        
        # ╨Ъ╨╛╤А╤А╨╡╨║╤В╨╕╤А╨╛╨▓╨║╨╕ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ ╨║╨╛╨╜╤В╨╡╨║╤Б╤В╨░
        match_minute = context.get('match_minute', 45)
        score_difference = context.get('score_difference', 0)
        team_situation = context.get('team_situation', 'drawing')
        importance = context.get('importance', 0.5)
        
        # ╨Т ╨║╨╛╨╜╤Ж╨╡ ╨╝╨░╤В╤З╨░ ╨┐╤А╨╕ ╨┐╤А╨╛╨╕╨│╤А╤Л╤И╨╡ - ╨▒╨╛╨╗╤М╤И╨╡ ╤А╨╕╤Б╨║╨░
        if match_minute > 75 and (score_difference < 0 or team_situation == 'losing'):
            risk_tendency += 0.25
        
        # ╨Т ╨▓╨░╨╢╨╜╤Л╤Е ╤Б╨╕╤В╤Г╨░╤Ж╨╕╤П╤Е - ╨▒╨╛╨╗╤М╤И╨╡ ╤А╨╕╤Б╨║╨░
        risk_tendency += importance * 0.15
        
        # ╨Я╤А╨╕ ╨▒╨╛╨╗╤М╤И╨╛╨╝ ╨┤╨░╨▓╨╗╨╡╨╜╨╕╨╕ - ╨╝╨╡╨╜╤М╤И╨╡ ╤А╨╕╤Б╨║╨░ (╨║╤А╨╛╨╝╨╡ ╨╛╤З╨╡╨╜╤М ╤Г╨▓╨╡╤А╨╡╨╜╨╜╤Л╤Е ╨╕╨│╤А╨╛╨║╨╛╨▓)
        pressure_level = context.get('pressure_level', 0.5)
        if pressure_level > 0.7:
            pressure_resistance = PersonalityModifier._get_trait_value(player, 'leadership')
            if pressure_resistance:
                resistance_modifier = PersonalityModifier._normalize_trait_value(pressure_resistance)
                pressure_penalty = 0.2 - (resistance_modifier * 0.15)
            else:
                pressure_penalty = 0.2
            risk_tendency -= pressure_penalty
        
        # ╨Ю╨│╤А╨░╨╜╨╕╤З╨╕╨▓╨░╨╡╨╝ ╨╖╨╜╨░╤З╨╡╨╜╨╕╤П
        risk_tendency = max(0.0, min(1.0, risk_tendency))
        
        # ╨б╤А╨░╨▓╨╜╨╕╨▓╨░╨╡╨╝ ╤Б ╤Г╤А╨╛╨▓╨╜╨╡╨╝ ╤А╨╕╤Б╨║╨░ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П
        return risk_tendency > (base_threshold + risk_level * 0.3)
    
    @staticmethod
    def evaluate_passing_options(player, passing_options, context=None):
        """
        ╨Ю╤Ж╨╡╨╜╨╕╨▓╨░╨╡╤В ╨▓╨░╤А╨╕╨░╨╜╤В╤Л ╨┐╨░╤Б╨╛╨▓ ╨╕ ╨▓╤Л╨▒╨╕╤А╨░╨╡╤В ╨╜╨░╨╕╨╗╤Г╤З╤И╨╕╨╣ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ personality.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            passing_options (list): ╨б╨┐╨╕╤Б╨╛╨║ ╨▓╨░╤А╨╕╨░╨╜╤В╨╛╨▓ ╨┐╨░╤Б╨░
                ╨Ъ╨░╨╢╨┤╤Л╨╣ ╤Н╨╗╨╡╨╝╨╡╨╜╤В - dict ╤Б ╨║╨╗╤О╤З╨░╨╝╨╕:
                - 'target_player': ╤Ж╨╡╨╗╨╡╨▓╨╛╨╣ ╨╕╨│╤А╨╛╨║
                - 'success_probability': ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╤М ╤Г╤Б╨┐╨╡╤Е╨░ (0.0-1.0)
                - 'risk_level': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╤А╨╕╤Б╨║╨░ (0.0-1.0)
                - 'pass_type': 'short', 'long', 'through'
                - 'potential_benefit': ╨┐╨╛╤В╨╡╨╜╤Ж╨╕╨░╨╗╤М╨╜╨░╤П ╨┐╨╛╨╗╤М╨╖╨░ (0.0-1.0)
            context (dict, optional): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕
                - 'pressure_level': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤П
                - 'time_remaining': ╨╛╤Б╤В╨░╨▓╤И╨╡╨╡╤Б╤П ╨▓╤А╨╡╨╝╤П
                - 'team_strategy': ╤Б╤В╤А╨░╤В╨╡╨│╨╕╤П ╨║╨╛╨╝╨░╨╜╨┤╤Л
            
        Returns:
            dict: ╨Т╤Л╨▒╤А╨░╨╜╨╜╤Л╨╣ ╨▓╨░╤А╨╕╨░╨╜╤В ╨┐╨░╤Б╨░ ╨╕╨╗╨╕ None ╨╡╤Б╨╗╨╕ ╨╜╨╡╤В ╨┐╨╛╨┤╤Е╨╛╨┤╤П╤Й╨╕╤Е
        
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
        
        # ╨Я╨╛╨╗╤Г╤З╨░╨╡╨╝ personality traits
        teamwork = PersonalityModifier._get_trait_value(player, 'teamwork')
        risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
        patience = PersonalityModifier._get_trait_value(player, 'patience')
        confidence = PersonalityModifier._get_trait_value(player, 'confidence')
        
        # ╨Т╨╡╤Б╨░ ╨┤╨╗╤П ╨╛╤Ж╨╡╨╜╨║╨╕ ╨┐╨░╤Б╨╛╨▓
        weights = {
            'success_probability': 0.4,  # ╨С╨░╨╖╨╛╨▓╤Л╨╣ ╨▓╨╡╤Б ╨┤╨╗╤П ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╨╕ ╤Г╤Б╨┐╨╡╤Е╨░
            'potential_benefit': 0.3,    # ╨Т╨╡╤Б ╨┤╨╗╤П ╨┐╨╛╤В╨╡╨╜╤Ж╨╕╨░╨╗╤М╨╜╨╛╨╣ ╨┐╨╛╨╗╤М╨╖╤Л
            'risk_penalty': 0.2,         # ╨и╤В╤А╨░╤Д ╨╖╨░ ╤А╨╕╤Б╨║
            'pass_type_preference': 0.1  # ╨Я╤А╨╡╨┤╨┐╨╛╤З╤В╨╡╨╜╨╕╨╡ ╤В╨╕╨┐╨░ ╨┐╨░╤Б╨░
        }
        
        # ╨Ъ╨╛╤А╤А╨╡╨║╤В╨╕╤А╤Г╨╡╨╝ ╨▓╨╡╤Б╨░ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ personality
        if teamwork:
            teamwork_modifier = PersonalityModifier._normalize_trait_value(teamwork)
            weights['success_probability'] += teamwork_modifier * 0.15  # ╨Ъ╨╛╨╝╨░╨╜╨┤╨╜╤Л╨╡ ╨╕╨│╤А╨╛╨║╨╕ ╤Ж╨╡╨╜╤П╤В ╨╜╨░╨┤╨╡╨╢╨╜╨╛╤Б╤В╤М
        
        if risk_taking:
            risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
            weights['potential_benefit'] += risk_modifier * 0.2   # ╨а╨╕╤Б╨║╨╛╨▓╨░╨╜╨╜╤Л╨╡ ╨╕╨│╤А╨╛╨║╨╕ ╤Ж╨╡╨╜╤П╤В ╨┐╨╛╨╗╤М╨╖╤Г
            weights['risk_penalty'] -= risk_modifier * 0.15      # ╨Ь╨╡╨╜╤М╤И╨╡ ╨▒╨╛╤П╤В╤Б╤П ╤А╨╕╤Б╨║╨░
        
        if patience:
            patience_modifier = PersonalityModifier._normalize_trait_value(patience)
            weights['success_probability'] += patience_modifier * 0.1  # ╨в╨╡╤А╨┐╨╡╨╗╨╕╨▓╤Л╨╡ ╤Ж╨╡╨╜╤П╤В ╨╜╨░╨┤╨╡╨╢╨╜╨╛╤Б╤В╤М
        
        if confidence:
            confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
            weights['risk_penalty'] -= confidence_modifier * 0.1  # ╨г╨▓╨╡╤А╨╡╨╜╨╜╤Л╨╡ ╨╝╨╡╨╜╤М╤И╨╡ ╨▒╨╛╤П╤В╤Б╤П ╤А╨╕╤Б╨║╨░
        
        # ╨Ю╤Ж╨╡╨╜╨╕╨▓╨░╨╡╨╝ ╨║╨░╨╢╨┤╤Л╨╣ ╨▓╨░╤А╨╕╨░╨╜╤В
        scored_options = []
        for option in passing_options:
            score = 0.0
            
            # ╨С╨░╨╖╨╛╨▓╨░╤П ╨╛╤Ж╨╡╨╜╨║╨░
            score += option.get('success_probability', 0.0) * weights['success_probability']
            score += option.get('potential_benefit', 0.0) * weights['potential_benefit']
            score -= option.get('risk_level', 0.0) * weights['risk_penalty']
            
            # ╨Я╤А╨╡╨┤╨┐╨╛╤З╤В╨╡╨╜╨╕╨╡ ╤В╨╕╨┐╨░ ╨┐╨░╤Б╨░
            pass_type = option.get('pass_type', 'short')
            type_preference = 0.0
            
            if pass_type == 'short' and patience:
                patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                type_preference = patience_modifier * 0.2
            elif pass_type in ['long', 'through'] and risk_taking:
                risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                type_preference = risk_modifier * 0.15
            
            score += type_preference * weights['pass_type_preference']
            
            # ╨Ъ╨╛╤А╤А╨╡╨║╤В╨╕╤А╨╛╨▓╨║╨╕ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ ╨║╨╛╨╜╤В╨╡╨║╤Б╤В╨░
            pressure_level = context.get('pressure_level', 0.5)
            if pressure_level > 0.7 and option.get('pass_type') == 'short':
                score += 0.1  # ╨Я╨╛╨┤ ╨┤╨░╨▓╨╗╨╡╨╜╨╕╨╡╨╝ ╨┐╤А╨╡╨┤╨┐╨╛╤З╨╕╤В╨░╨╡╨╝ ╨┐╤А╨╛╤Б╤В╤Л╨╡ ╨┐╨░╤Б╤Л
            
            scored_options.append((option, score))
        
        # ╨б╨╛╤А╤В╨╕╤А╤Г╨╡╨╝ ╨┐╨╛ ╨╛╤Ж╨╡╨╜╨║╨╡
        scored_options.sort(key=lambda x: x[1], reverse=True)
        
        # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╨╝╨╕╨╜╨╕╨╝╨░╨╗╤М╨╜╤Л╨╣ ╨┐╨╛╤А╨╛╨│ ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╨╕
        best_option, best_score = scored_options[0]
        min_confidence = PersonalityDecisionEngine.DECISION_THRESHOLDS['pass_confidence']
        
        if best_score >= min_confidence:
            return best_option
        
        return None
    
    @staticmethod
    def decide_shot_timing(player, shot_opportunity, context=None):
        """
        ╨Я╤А╨╕╨╜╨╕╨╝╨░╨╡╤В ╤А╨╡╤И╨╡╨╜╨╕╨╡ ╨╛ ╨▓╤А╨╡╨╝╨╡╨╜╨╕ ╤Г╨┤╨░╤А╨░ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ personality ╨╕ ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            shot_opportunity (dict): ╨Ш╨╜╤Д╨╛╤А╨╝╨░╤Ж╨╕╤П ╨╛ ╨▓╨╛╨╖╨╝╨╛╨╢╨╜╨╛╤Б╤В╨╕ ╤Г╨┤╨░╤А╨░
                - 'success_probability': ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╤М ╨┐╨╛╨┐╨░╨┤╨░╨╜╨╕╤П (0.0-1.0)
                - 'goal_distance': ╤А╨░╤Б╤Б╤В╨╛╤П╨╜╨╕╨╡ ╨┤╨╛ ╨▓╨╛╤А╨╛╤В
                - 'angle': ╤Г╨│╨╛╨╗ ╨║ ╨▓╨╛╤А╨╛╤В╨░╨╝
                - 'pressure_level': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤П
                - 'shot_type': 'close', 'long', 'header', 'volley'
            context (dict, optional): ╨Ф╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╤Л╨╣ ╨║╨╛╨╜╤В╨╡╨║╤Б╤В
                - 'alternative_actions': ╨░╨╗╤М╤В╨╡╤А╨╜╨░╤В╨╕╨▓╨╜╤Л╨╡ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П
                - 'match_minute': ╨╝╨╕╨╜╤Г╤В╨░ ╨╝╨░╤В╤З╨░
                - 'score_difference': ╤А╨░╨╖╨╜╨╛╤Б╤В╤М ╨▓ ╤Б╤З╨╡╤В╨╡
                - 'team_momentum': ╨╕╨╝╨┐╤Г╨╗╤М╤Б ╨║╨╛╨╝╨░╨╜╨┤╤Л
            
        Returns:
            str: ╨а╨╡╤И╨╡╨╜╨╕╨╡ ('shoot_now', 'wait_for_better', 'pass_instead')
        
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
        
        # ╨Я╨╛╨╗╤Г╤З╨░╨╡╨╝ personality traits
        ambition = PersonalityModifier._get_trait_value(player, 'ambition')
        patience = PersonalityModifier._get_trait_value(player, 'patience')
        confidence = PersonalityModifier._get_trait_value(player, 'confidence')
        risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
        
        # ╨С╨░╨╖╨╛╨▓╨░╤П ╨╛╤Ж╨╡╨╜╨║╨░ ╨▓╨╛╨╖╨╝╨╛╨╢╨╜╨╛╤Б╤В╨╕ ╤Г╨┤╨░╤А╨░
        shot_quality = shot_opportunity.get('success_probability', 0.0)
        base_threshold = PersonalityDecisionEngine.DECISION_THRESHOLDS['shot_timing']
        
        # ╨Ъ╨╛╤А╤А╨╡╨║╤В╨╕╤А╤Г╨╡╨╝ ╨┐╨╛╤А╨╛╨│ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ personality
        threshold = base_threshold
        
        if ambition:
            ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
            threshold -= ambition_modifier * 0.2  # ╨Р╨╝╨▒╨╕╤Ж╨╕╨╛╨╖╨╜╤Л╨╡ ╤Б╤В╤А╨╡╨╗╤П╤О╤В ╨┐╤А╨╕ ╨╝╨╡╨╜╤М╤И╨╕╤Е ╤И╨░╨╜╤Б╨░╤Е
        
        if patience:
            patience_modifier = PersonalityModifier._normalize_trait_value(patience)
            threshold += patience_modifier * 0.15  # ╨в╨╡╤А╨┐╨╡╨╗╨╕╨▓╤Л╨╡ ╨╢╨┤╤Г╤В ╨╗╤Г╤З╤И╨╕╤Е ╨╝╨╛╨╝╨╡╨╜╤В╨╛╨▓
        
        if confidence:
            confidence_modifier = PersonalityModifier._normalize_trait_value(confidence)
            # ╨г╨▓╨╡╤А╨╡╨╜╨╜╤Л╨╡ ╨╕╨│╤А╨╛╨║╨╕ ╨║╨╛╤А╤А╨╡╨║╤В╨╕╤А╤Г╤О╤В ╨▓╨╛╤Б╨┐╤А╨╕╨╜╨╕╨╝╨░╨╡╨╝╨╛╨╡ ╨║╨░╤З╨╡╤Б╤В╨▓╨╛ ╤Г╨┤╨░╤А╨░
            shot_quality += confidence_modifier * 0.1
        
        # ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В╨╜╤Л╨╡ ╤Д╨░╨║╤В╨╛╤А╤Л
        match_minute = context.get('match_minute', 45)
        score_difference = context.get('score_difference', 0)
        pressure_level = shot_opportunity.get('pressure_level', 0.5)
        shot_type = shot_opportunity.get('shot_type', 'close')
        
        # ╨Т ╨║╨╛╨╜╤Ж╨╡ ╨╝╨░╤В╤З╨░ ╨┐╤А╨╕ ╨┐╤А╨╛╨╕╨│╤А╤Л╤И╨╡ - ╤Б╤В╤А╨╡╨╗╤П╨╡╨╝ ╤З╨░╤Й╨╡
        if match_minute > 70 and score_difference < 0:
            urgency_factor = (match_minute - 70) / 20.0  # ╨г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В╤Б╤П ╨║ ╨║╨╛╨╜╤Ж╤Г
            threshold -= urgency_factor * 0.3
        
        # ╨Я╤А╨╕ ╨▓╤Л╤Б╨╛╨║╨╛╨╝ ╨┤╨░╨▓╨╗╨╡╨╜╨╕╨╕ - ╨▒╤Л╤Б╤В╤А╨╡╨╡ ╨┐╤А╨╕╨╜╨╕╨╝╨░╨╡╨╝ ╤А╨╡╤И╨╡╨╜╨╕╨╡
        if pressure_level > 0.7:
            threshold -= 0.1
        
        # ╨б╨┐╨╡╤Ж╨╕╨░╨╗╤М╨╜╤Л╨╡ ╤Б╨╗╤Г╤З╨░╨╕ ╨┤╨╗╤П ╤В╨╕╨┐╨╛╨▓ ╤Г╨┤╨░╤А╨╛╨▓
        if shot_type == 'long' and risk_taking:
            risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
            threshold -= risk_modifier * 0.1  # ╨Ы╤О╨▒╨╕╤В╨╡╨╗╨╕ ╤А╨╕╤Б╨║╨░ ╤З╨░╤Й╨╡ ╨▒╤М╤О╤В ╨╕╨╖╨┤╨░╨╗╨╡╨║╨░
        
        # ╨Я╤А╨╕╨╜╨╕╨╝╨░╨╡╨╝ ╤А╨╡╤И╨╡╨╜╨╕╨╡
        if shot_quality >= threshold:
            return 'shoot_now'
        elif shot_quality >= threshold - 0.2:
            # ╨С╨╗╨╕╨╖╨║╨╛ ╨║ ╨┐╨╛╤А╨╛╨│╤Г - ╨┐╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╨░╨╗╤М╤В╨╡╤А╨╜╨░╤В╨╕╨▓╤Л
            alternatives = context.get('alternative_actions', [])
            
            # ╨Х╤Б╨╗╨╕ ╨╡╤Б╤В╤М ╤Е╨╛╤А╨╛╤И╨╕╨╡ ╨░╨╗╤М╤В╨╡╤А╨╜╨░╤В╨╕╨▓╤Л ╨╕ ╨╕╨│╤А╨╛╨║ ╤В╨╡╤А╨┐╨╡╨╗╨╕╨▓ - ╨╢╨┤╨╡╨╝
            if alternatives and patience:
                patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                if patience_modifier > 0.1:
                    return 'wait_for_better'
            
            return 'shoot_now'
        else:
            # ╨Э╨╕╨╖╨║╨╛╨╡ ╨║╨░╤З╨╡╤Б╤В╨▓╨╛ ╤Г╨┤╨░╤А╨░
            if ambition:
                ambition_modifier = PersonalityModifier._normalize_trait_value(ambition)
                # ╨Ю╤З╨╡╨╜╤М ╨░╨╝╨▒╨╕╤Ж╨╕╨╛╨╖╨╜╤Л╨╡ ╨╝╨╛╨│╤Г╤В ╤Б╤В╤А╨╡╨╗╤П╤В╤М ╨┤╨░╨╢╨╡ ╨┐╤А╨╕ ╨╜╨╕╨╖╨║╨╕╤Е ╤И╨░╨╜╤Б╨░╤Е
                if ambition_modifier > 0.15 and random.random() < 0.3:
                    return 'shoot_now'
            
            return 'pass_instead'
    
    @staticmethod
    def get_decision_confidence(player, action_type, context=None):
        """
        ╨Т╤Л╤З╨╕╤Б╨╗╤П╨╡╤В ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М ╨╕╨│╤А╨╛╨║╨░ ╨▓ ╨┐╤А╨╕╨╜╤П╤В╨╛╨╝ ╤А╨╡╤И╨╡╨╜╨╕╨╕.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            action_type (str): ╨в╨╕╨┐ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П
            context (dict, optional): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕
                - 'situation_familiarity': ╨╖╨╜╨░╨║╨╛╨╝╨╛╤Б╤В╤М ╤Б ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╡╨╣ (0.0-1.0)
                - 'pressure_level': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┤╨░╨▓╨╗╨╡╨╜╨╕╤П
                - 'support_level': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┐╨╛╨┤╨┤╨╡╤А╨╢╨║╨╕ ╨║╨╛╨╝╨░╨╜╨┤╤Л
                - 'match_importance': ╨▓╨░╨╢╨╜╨╛╤Б╤В╤М ╨╝╨░╤В╤З╨░
            
        Returns:
            float: ╨г╤А╨╛╨▓╨╡╨╜╤М ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╨╕ ╨▓ ╤А╨╡╤И╨╡╨╜╨╕╨╕ (0.0-1.0)
        
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
        
        # ╨С╨░╨╖╨╛╨▓╨░╤П ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М
        base_confidence = 0.5
        
        # ╨Я╨╛╨╗╤Г╤З╨░╨╡╨╝ personality traits
        confidence_trait = PersonalityModifier._get_trait_value(player, 'confidence')
        leadership = PersonalityModifier._get_trait_value(player, 'leadership')
        experience = PersonalityModifier._get_trait_value(player, 'adaptability')
        
        # ╨Ю╤Б╨╜╨╛╨▓╨╜╤Л╨╡ ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╨╕
        if confidence_trait:
            confidence_modifier = PersonalityModifier._normalize_trait_value(confidence_trait)
            base_confidence += confidence_modifier * 0.3  # ╨б╨╕╨╗╤М╨╜╨╛╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡
        
        if leadership:
            leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
            base_confidence += leadership_modifier * 0.15  # ╨Ы╨╕╨┤╨╡╤А╤Л ╨▒╨╛╨╗╨╡╨╡ ╤Г╨▓╨╡╤А╨╡╨╜╤Л
        
        if experience:
            experience_modifier = PersonalityModifier._normalize_trait_value(experience)
            base_confidence += experience_modifier * 0.1  # ╨Ю╨┐╤Л╤В ╨┤╨╛╨▒╨░╨▓╨╗╤П╨╡╤В ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╨╕
        
        # ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В╨╜╤Л╨╡ ╤Д╨░╨║╤В╨╛╤А╤Л
        situation_familiarity = context.get('situation_familiarity', 0.5)
        pressure_level = context.get('pressure_level', 0.5)
        support_level = context.get('support_level', 0.5)
        match_importance = context.get('match_importance', 0.5)
        
        # ╨Ч╨╜╨░╨║╨╛╨╝╨╛╤Б╤В╤М ╤Б ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╡╨╣ ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М
        base_confidence += (situation_familiarity - 0.5) * 0.2
        
        # ╨Ф╨░╨▓╨╗╨╡╨╜╨╕╨╡ ╤Б╨╜╨╕╨╢╨░╨╡╤В ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М (╨║╤А╨╛╨╝╨╡ ╤Б╤В╤А╨╡╤Б╤Б╨╛╤Г╤Б╤В╨╛╨╣╤З╨╕╨▓╤Л╤Е)
        pressure_penalty = (pressure_level - 0.5) * 0.25
        if leadership:
            leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
            pressure_penalty *= (1.0 - leadership_modifier * 0.5)  # ╨Ы╨╕╨┤╨╡╤А╤Л ╨╗╤Г╤З╤И╨╡ ╤Б╨┐╤А╨░╨▓╨╗╤П╤О╤В╤Б╤П ╤Б ╨┤╨░╨▓╨╗╨╡╨╜╨╕╨╡╨╝
        base_confidence -= pressure_penalty
        
        # ╨Я╨╛╨┤╨┤╨╡╤А╨╢╨║╨░ ╨║╨╛╨╝╨░╨╜╨┤╤Л ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╤В ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М
        base_confidence += (support_level - 0.5) * 0.15
        
        # ╨Т╨░╨╢╨╜╨╛╤Б╤В╤М ╨╝╨░╤В╤З╨░ ╨╝╨╛╨╢╨╡╤В ╨║╨░╨║ ╤Г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╤В╤М, ╤В╨░╨║ ╨╕ ╤Б╨╜╨╕╨╢╨░╤В╤М ╤Г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М
        if match_importance > 0.7:
            if confidence_trait and PersonalityModifier._normalize_trait_value(confidence_trait) > 0.1:
                base_confidence += 0.1  # ╨г╨▓╨╡╤А╨╡╨╜╨╜╤Л╨╡ ╨╕╨│╤А╨╛╨║╨╕ ╨╝╨╛╤В╨╕╨▓╨╕╤А╤Г╤О╤В╤Б╤П ╨▓╨░╨╢╨╜╨╛╤Б╤В╤М╤О
            else:
                base_confidence -= 0.1  # ╨Э╨╡╤Г╨▓╨╡╤А╨╡╨╜╨╜╤Л╨╡ ╨╕╨│╤А╨╛╨║╨╕ ╨╜╨╡╤А╨▓╨╜╨╕╤З╨░╤О╤В
        
        # ╨б╨┐╨╡╤Ж╨╕╤Д╨╕╤З╨╡╤Б╨║╨╕╨╡ ╨╝╨╛╨┤╨╕╤Д╨╕╨║╨░╤В╨╛╤А╤Л ╨┤╨╗╤П ╤В╨╕╨┐╨╛╨▓ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╨╣
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
        
        # ╨Ю╨│╤А╨░╨╜╨╕╤З╨╕╨▓╨░╨╡╨╝ ╨╖╨╜╨░╤З╨╡╨╜╨╕╤П
        return max(0.0, min(1.0, base_confidence))
    
    @staticmethod
    def evaluate_tactical_decision(player, tactical_options, context=None):
        """
        ╨Ю╤Ж╨╡╨╜╨╕╨▓╨░╨╡╤В ╤В╨░╨║╤В╨╕╤З╨╡╤Б╨║╨╕╨╡ ╤А╨╡╤И╨╡╨╜╨╕╤П ╨╕╨│╤А╨╛╨║╨░ ╨▓ ╤Б╨╗╨╛╨╢╨╜╤Л╤Е ╤Б╨╕╤В╤Г╨░╤Ж╨╕╤П╤Е.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            tactical_options (list): ╨б╨┐╨╕╤Б╨╛╨║ ╤В╨░╨║╤В╨╕╤З╨╡╤Б╨║╨╕╤Е ╨▓╨░╤А╨╕╨░╨╜╤В╨╛╨▓
                ╨Ъ╨░╨╢╨┤╤Л╨╣ ╤Н╨╗╨╡╨╝╨╡╨╜╤В - dict ╤Б ╨║╨╗╤О╤З╨░╨╝╨╕:
                - 'option_type': ╤В╨╕╨┐ ╨▓╨░╤А╨╕╨░╨╜╤В╨░
                - 'success_probability': ╨▓╨╡╤А╨╛╤П╤В╨╜╨╛╤Б╤В╤М ╤Г╤Б╨┐╨╡╤Е╨░
                - 'risk_level': ╤Г╤А╨╛╨▓╨╡╨╜╤М ╤А╨╕╤Б╨║╨░
                - 'team_benefit': ╨┐╨╛╨╗╤М╨╖╨░ ╨┤╨╗╤П ╨║╨╛╨╝╨░╨╜╨┤╤Л
                - 'personal_benefit': ╨╗╨╕╤З╨╜╨░╤П ╨┐╨╛╨╗╤М╨╖╨░
            context (dict, optional): ╨в╨░╨║╤В╨╕╤З╨╡╤Б╨║╨╕╨╣ ╨║╨╛╨╜╤В╨╡╨║╤Б╤В
                - 'team_strategy': ╤Б╤В╤А╨░╤В╨╡╨│╨╕╤П ╨║╨╛╨╝╨░╨╜╨┤╤Л
                - 'opponent_weakness': ╤Б╨╗╨░╨▒╨╛╤Б╤В╤М ╨┐╤А╨╛╤В╨╕╨▓╨╜╨╕╨║╨░
                - 'match_phase': ╤Д╨░╨╖╨░ ╨╝╨░╤В╤З╨░
                - 'score_situation': ╤Б╨╕╤В╤Г╨░╤Ж╨╕╤П ╤Б╨╛ ╤Б╤З╨╡╤В╨╛╨╝
        
        Returns:
            dict: ╨Т╤Л╨▒╤А╨░╨╜╨╜╤Л╨╣ ╤В╨░╨║╤В╨╕╤З╨╡╤Б╨║╨╕╨╣ ╨▓╨░╤А╨╕╨░╨╜╤В
        
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
        
        # ╨Я╨╛╨╗╤Г╤З╨░╨╡╨╝ ╨║╨╗╤О╤З╨╡╨▓╤Л╨╡ personality traits ╨┤╨╗╤П ╤В╨░╨║╤В╨╕╤З╨╡╤Б╨║╨╕╤Е ╤А╨╡╤И╨╡╨╜╨╕╨╣
        teamwork = PersonalityModifier._get_trait_value(player, 'teamwork')
        ambition = PersonalityModifier._get_trait_value(player, 'ambition')
        risk_taking = PersonalityModifier._get_trait_value(player, 'risk_taking')
        leadership = PersonalityModifier._get_trait_value(player, 'leadership')
        patience = PersonalityModifier._get_trait_value(player, 'patience')
        
        # ╨Т╨╡╤Б╨░ ╨┤╨╗╤П ╨╛╤Ж╨╡╨╜╨║╨╕ ╤В╨░╨║╤В╨╕╤З╨╡╤Б╨║╨╕╤Е ╤А╨╡╤И╨╡╨╜╨╕╨╣
        weights = {
            'success_probability': 0.3,
            'team_benefit': 0.25,
            'personal_benefit': 0.15,
            'risk_factor': 0.2,
            'leadership_factor': 0.1
        }
        
        # ╨Ъ╨╛╤А╤А╨╡╨║╤В╨╕╤А╤Г╨╡╨╝ ╨▓╨╡╤Б╨░ ╨╜╨░ ╨╛╤Б╨╜╨╛╨▓╨╡ personality
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
        
        # ╨Ю╤Ж╨╡╨╜╨╕╨▓╨░╨╡╨╝ ╨║╨░╨╢╨┤╤Л╨╣ ╤В╨░╨║╤В╨╕╤З╨╡╤Б╨║╨╕╨╣ ╨▓╨░╤А╨╕╨░╨╜╤В
        scored_options = []
        for option in tactical_options:
            score = 0.0
            
            # ╨С╨░╨╖╨╛╨▓╤Л╨╡ ╤Д╨░╨║╤В╨╛╤А╤Л
            score += option.get('success_probability', 0.0) * weights['success_probability']
            score += option.get('team_benefit', 0.0) * weights['team_benefit']
            score += option.get('personal_benefit', 0.0) * weights['personal_benefit']
            
            # ╨д╨░╨║╤В╨╛╤А ╤А╨╕╤Б╨║╨░ (╨╝╨╛╨╢╨╡╤В ╨▒╤Л╤В╤М ╨║╨░╨║ ╨┐╨╛╨╗╨╛╨╢╨╕╤В╨╡╨╗╤М╨╜╤Л╨╝, ╤В╨░╨║ ╨╕ ╨╛╤В╤А╨╕╤Ж╨░╤В╨╡╨╗╤М╨╜╤Л╨╝)
            risk_level = option.get('risk_level', 0.0)
            if risk_taking:
                risk_modifier = PersonalityModifier._normalize_trait_value(risk_taking)
                risk_impact = risk_modifier * risk_level * weights['risk_factor']
            else:
                risk_impact = -risk_level * weights['risk_factor']  # ╨и╤В╤А╨░╤Д ╨╖╨░ ╤А╨╕╤Б╨║
            score += risk_impact
            
            # ╨Ы╨╕╨┤╨╡╤А╤Б╨║╨╕╨╡ ╤А╨╡╤И╨╡╨╜╨╕╤П
            if leadership and option.get('option_type') in ['lead_by_example', 'organize_team', 'motivate_teammates']:
                leadership_modifier = PersonalityModifier._normalize_trait_value(leadership)
                score += leadership_modifier * weights['leadership_factor']
            
            # ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В╨╜╤Л╨╡ ╨║╨╛╤А╤А╨╡╨║╤В╨╕╤А╨╛╨▓╨║╨╕
            match_phase = context.get('match_phase', 'middle')
            score_situation = context.get('score_situation', 'drawing')
            
            if match_phase == 'late' and score_situation == 'losing':
                if option.get('option_type') in ['aggressive_press', 'risky_attack']:
                    score += 0.15  # ╨С╨╛╨╜╤Г╤Б ╨╖╨░ ╨░╨│╤А╨╡╤Б╤Б╨╕╨▓╨╜╤Л╨╡ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П ╨┐╤А╨╕ ╨┐╤А╨╛╨╕╨│╤А╤Л╤И╨╡
            
            if patience and option.get('option_type') in ['patient_buildup', 'wait_for_opportunity']:
                patience_modifier = PersonalityModifier._normalize_trait_value(patience)
                score += patience_modifier * 0.1
            
            scored_options.append((option, score))
        
        # ╨Т╤Л╨▒╨╕╤А╨░╨╡╨╝ ╨╗╤Г╤З╤И╨╕╨╣ ╨▓╨░╤А╨╕╨░╨╜╤В
        scored_options.sort(key=lambda x: x[1], reverse=True)
        return scored_options[0][0] if scored_options else None
    
    @staticmethod
    def get_influencing_trait(player, action_type, context=None):
        """
        ╨Ю╨┐╤А╨╡╨┤╨╡╨╗╤П╨╡╤В ╨╛╤Б╨╜╨╛╨▓╨╜╤Г╤О ╤З╨╡╤А╤В╤Г ╤Е╨░╤А╨░╨║╤В╨╡╤А╨░, ╨▓╨╗╨╕╤П╤О╤Й╤Г╤О ╨╜╨░ ╨┐╤А╨╕╨╜╤П╤В╨╛╨╡ ╤А╨╡╤И╨╡╨╜╨╕╨╡.
        
        Args:
            player: ╨Ю╨▒╤К╨╡╨║╤В ╨╕╨│╤А╨╛╨║╨░
            action_type (str): ╨в╨╕╨┐ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П ('pass', 'shoot', 'dribble', 'tackle', 'long_pass', 'attack')
            context (dict, optional): ╨Ъ╨╛╨╜╤В╨╡╨║╤Б╤В ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╤Б╨╕╤В╤Г╨░╤Ж╨╕╨╕
            
        Returns:
            tuple: (trait_name, trait_description) ╨╕╨╗╨╕ (None, None) ╨╡╤Б╨╗╨╕ ╨╜╨╡╤В ╨▓╨╗╨╕╤П╨╜╨╕╤П
        """
        if not getattr(settings, 'USE_PERSONALITY_ENGINE', False):
            return (None, None)
        
        try:
            # ╨б╨╗╨╛╨▓╨░╤А╤М ╤Б ╨╛╨┐╨╕╤Б╨░╨╜╨╕╤П╨╝╨╕ ╤З╨╡╤А╤В ╤Е╨░╤А╨░╨║╤В╨╡╤А╨░ ╨╜╨░ ╤А╤Г╤Б╤Б╨║╨╛╨╝
            TRAIT_DESCRIPTIONS = {
                'aggression': '╨Р╨│╤А╨╡╤Б╤Б╨╕╨▓╨╜╨╛╤Б╤В╤М',
                'confidence': '╨г╨▓╨╡╤А╨╡╨╜╨╜╨╛╤Б╤В╤М',
                'risk_taking': '╨б╨║╨╗╨╛╨╜╨╜╨╛╤Б╤В╤М ╨║ ╤А╨╕╤Б╨║╤Г',
                'patience': '╨в╨╡╤А╨┐╨╡╨╗╨╕╨▓╨╛╤Б╤В╤М',
                'teamwork': '╨Ъ╨╛╨╝╨░╨╜╨┤╨╜╨░╤П ╨╕╨│╤А╨░',
                'leadership': '╨Ы╨╕╨┤╨╡╤А╤Б╤В╨▓╨╛',
                'ambition': '╨Р╨╝╨▒╨╕╤Ж╨╕╨╛╨╖╨╜╨╛╤Б╤В╤М',
                'charisma': '╨е╨░╤А╨╕╨╖╨╝╨░',
                'endurance': '╨Т╤Л╨╜╨╛╤Б╨╗╨╕╨▓╨╛╤Б╤В╤М',
                'adaptability': '╨Р╨┤╨░╨┐╤В╨╕╨▓╨╜╨╛╤Б╤В╤М'
            }
            
            # ╨Ю╨┐╤А╨╡╨┤╨╡╨╗╤П╨╡╨╝ ╨╛╤Б╨╜╨╛╨▓╨╜╤Г╤О ╤З╨╡╤А╤В╤Г ╨┤╨╗╤П ╨║╨░╨╢╨┤╨╛╨│╨╛ ╤В╨╕╨┐╨░ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П
            trait_mapping = {
                'shoot': ['ambition', 'confidence', 'risk_taking'],
                'pass': ['teamwork', 'patience'],
                'long_pass': ['risk_taking', 'ambition'],
                'dribble': ['confidence', 'risk_taking'],
                'tackle': ['aggression'],
                'attack': ['ambition', 'risk_taking']
            }
            
            # ╨Я╨╛╨╗╤Г╤З╨░╨╡╨╝ ╤З╨╡╤А╤В╤Л ╨┤╨╗╤П ╨┤╨░╨╜╨╜╨╛╨│╨╛ ╨┤╨╡╨╣╤Б╤В╨▓╨╕╤П
            relevant_traits = trait_mapping.get(action_type, [])
            if not relevant_traits:
                return (None, None)
            
            # ╨Э╨░╤Е╨╛╨┤╨╕╨╝ ╤З╨╡╤А╤В╤Г ╤Б ╨╜╨░╨╕╨▒╨╛╨╗╤М╤И╨╕╨╝ ╨╖╨╜╨░╤З╨╡╨╜╨╕╨╡╨╝ ╤Г ╨╕╨│╤А╨╛╨║╨░
            max_trait = None
            max_value = 0
            
            for trait in relevant_traits:
                trait_value = PersonalityModifier._get_trait_value(player, trait)
                if trait_value and trait_value > max_value:
                    max_value = trait_value
                    max_trait = trait
            
            # ╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╨╝ ╤З╨╡╤А╤В╤Г ╤В╨╛╨╗╤М╨║╨╛ ╨╡╤Б╨╗╨╕ ╨╡╤С ╨╖╨╜╨░╤З╨╡╨╜╨╕╨╡ ╨┤╨╛╤Б╤В╨░╤В╨╛╤З╨╜╨╛ ╨▓╤Л╤Б╨╛╨║╨╛╨╡ (>12)
            if max_trait and max_value > 3:
                return (max_trait, TRAIT_DESCRIPTIONS.get(max_trait, max_trait))
            
            return (None, None)
            
        except Exception as e:
            logger.warning(f"Error getting influencing trait for player {player.id}: {e}")
            return (None, None)
