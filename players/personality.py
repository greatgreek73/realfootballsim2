"""
Personality system for players.

This module defines personality traits structure and provides
generation functionality for player personalities.
"""

import random


# Personality traits structure definition
PERSONALITY_TRAITS_STRUCTURE = {
    'mental': {
        'aggression': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s tendency to be aggressive in challenges and decisions'
        },
        'ambition': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s drive to succeed and achieve goals'
        },
        'confidence': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s self-belief and mental strength'
        },
        'leadership': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s ability to lead and influence teammates'
        }
    },
    'social': {
        'teamwork': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s ability to work effectively with teammates'
        },
        'charisma': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s ability to inspire and motivate others'
        },
        'patience': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s ability to remain calm and composed under pressure'
        }
    },
    'physical': {
        'risk_taking': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s willingness to take risks in play'
        },
        'endurance': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s mental stamina and persistence'
        },
        'adaptability': {
            'min': 1,
            'max': 20,
            'description': 'Player\'s ability to adapt to new situations and tactics'
        }
    }
}


class PersonalityGenerator:
    """
    Generator for player personality traits.
    
    Provides methods to generate random personality values
    within defined ranges for all personality traits.
    """
    
    @staticmethod
    def generate():
        """
        Generate a complete set of personality traits with random values.
        
        Returns:
            dict: Dictionary with trait names as keys and random values (1-20) as values
            
        Example:
            {
                'aggression': 15,
                'ambition': 8,
                'confidence': 12,
                'leadership': 6,
                'teamwork': 18,
                'charisma': 9,
                'patience': 14,
                'risk_taking': 11,
                'endurance': 16,
                'adaptability': 7
            }
        """
        personality = {}
        
        # Generate random values for all traits
        for category_traits in PERSONALITY_TRAITS_STRUCTURE.values():
            for trait_name, trait_config in category_traits.items():
                personality[trait_name] = random.randint(
                    trait_config['min'], 
                    trait_config['max']
                )
        
        return personality
    
    @staticmethod
    def get_trait_description(trait_name):
        """
        Get description for a specific personality trait.
        
        Args:
            trait_name (str): Name of the personality trait
            
        Returns:
            str: Description of the trait, or None if not found
        """
        for category_traits in PERSONALITY_TRAITS_STRUCTURE.values():
            if trait_name in category_traits:
                return category_traits[trait_name]['description']
        return None
    
    @staticmethod
    def get_all_trait_names():
        """
        Get list of all available personality trait names.
        
        Returns:
            list: List of all trait names
        """
        trait_names = []
        for category_traits in PERSONALITY_TRAITS_STRUCTURE.values():
            trait_names.extend(category_traits.keys())
        return trait_names