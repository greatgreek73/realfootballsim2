"""
Personality Modifiers Configuration

This module defines how personality traits influence player behavior and decision-making
during match simulation. Each modifier represents the impact of a specific personality
trait on various game actions and situations.

Modifier values are balanced for 40% realism and 60% gameplay impact:
- Values range from -0.3 to +0.3 for moderate effects
- Critical traits can have values up to ±0.5 for significant impact
- All modifiers are multiplicative with base probabilities

Usage:
    from matches.personality_modifiers import get_modifier_by_trait, get_situation_modifiers
    
    # Get passing modifier for aggressive player
    modifier = get_modifier_by_trait('aggressive', 'forward_pass')
    
    # Get modifiers for penalty situation
    modifiers = get_situation_modifiers('penalty_kick')
"""

# =============================================================================
# PASSING MODIFIERS
# Influence on passing decisions and accuracy
# =============================================================================

PASSING_MODIFIERS = {
    'aggressive': {
        'forward_pass': 0.25,      # More likely to attempt forward passes
        'through_pass': 0.30,      # Higher tendency for risky through balls
        'cross_attempt': 0.20,     # More crossing attempts
        'pass_accuracy': -0.10,    # Slightly reduced accuracy due to risk-taking
        'long_pass': 0.25,         # Prefers long passes over short ones
        'quick_pass': 0.15,        # Faster decision making
    },
    'cautious': {
        'forward_pass': -0.25,     # Prefers safe backward/sideways passes
        'through_pass': -0.35,     # Avoids risky through balls
        'cross_attempt': -0.15,    # Less likely to cross
        'pass_accuracy': 0.20,     # Higher accuracy due to safe choices
        'long_pass': -0.20,        # Prefers shorter, safer passes
        'quick_pass': -0.20,       # Takes more time to decide
    },
    'creative': {
        'forward_pass': 0.15,      # Good balance of forward play
        'through_pass': 0.40,      # Excellent at finding key passes
        'cross_attempt': 0.25,     # Creative crossing opportunities
        'pass_accuracy': 0.10,     # Good technique
        'long_pass': 0.20,         # Can spot long-range opportunities
        'quick_pass': 0.25,        # Quick thinking
    },
    'selfish': {
        'forward_pass': -0.15,     # Less likely to pass forward (wants ball)
        'through_pass': -0.30,     # Rarely assists others
        'cross_attempt': -0.25,    # Prefers to cut inside
        'pass_accuracy': -0.05,    # Slight reduction in focus
        'long_pass': -0.10,        # Prefers to keep ball close
        'quick_pass': -0.15,       # Holds onto ball longer
    },
    'team_player': {
        'forward_pass': 0.20,      # Good team play
        'through_pass': 0.25,      # Sets up teammates
        'cross_attempt': 0.15,     # Good crossing for team
        'pass_accuracy': 0.15,     # Focused on team success
        'long_pass': 0.10,         # Good distribution
        'quick_pass': 0.20,        # Quick ball movement
    },
    'confident': {
        'forward_pass': 0.20,      # Not afraid of forward passes
        'through_pass': 0.25,      # Attempts difficult passes
        'cross_attempt': 0.15,     # Confident in crossing
        'pass_accuracy': 0.05,     # Slight boost from confidence
        'long_pass': 0.15,         # Attempts longer passes
        'quick_pass': 0.10,        # Decisive passing
    },
    'nervous': {
        'forward_pass': -0.20,     # Prefers safe options
        'through_pass': -0.30,     # Avoids risky passes
        'cross_attempt': -0.20,    # Less likely to cross
        'pass_accuracy': -0.15,    # Nervousness affects accuracy
        'long_pass': -0.25,        # Avoids long passes
        'quick_pass': -0.25,       # Hesitant decision making
    },
}

# =============================================================================
# SHOOTING MODIFIERS
# Influence on shooting decisions and accuracy
# =============================================================================

SHOOTING_MODIFIERS = {
    'aggressive': {
        'shot_attempt': 0.35,      # Much more likely to shoot
        'long_shot': 0.40,         # Attempts shots from distance
        'shot_accuracy': -0.05,    # Slight reduction due to forcing shots
        'shot_power': 0.20,        # Hits harder shots
        'composure': -0.10,        # May rush shots
    },
    'cautious': {
        'shot_attempt': -0.30,     # Much less likely to shoot
        'long_shot': -0.40,        # Avoids speculative shots
        'shot_accuracy': 0.15,     # Better accuracy when shooting
        'shot_power': -0.10,       # More controlled shots
        'composure': 0.20,         # Calmer in front of goal
    },
    'creative': {
        'shot_attempt': 0.15,      # Good shooting instincts
        'long_shot': 0.25,         # Can spot opportunities
        'shot_accuracy': 0.20,     # Excellent technique
        'shot_power': 0.10,        # Good power control
        'composure': 0.25,         # Creative finishing
    },
    'selfish': {
        'shot_attempt': 0.45,      # Very high shooting tendency
        'long_shot': 0.35,         # Will shoot from anywhere
        'shot_accuracy': -0.10,    # Forces difficult shots
        'shot_power': 0.15,        # Powerful shots
        'composure': -0.15,        # May be selfish in key moments
    },
    'team_player': {
        'shot_attempt': -0.10,     # May pass instead of shoot
        'long_shot': -0.15,        # Prefers to work ball closer
        'shot_accuracy': 0.10,     # Good when shooting
        'shot_power': 0.05,        # Balanced approach
        'composure': 0.15,         # Team-focused composure
    },
    'confident': {
        'shot_attempt': 0.25,      # Confident to shoot
        'long_shot': 0.30,         # Backs himself from distance
        'shot_accuracy': 0.15,     # Confidence improves accuracy
        'shot_power': 0.15,        # Confident strikes
        'composure': 0.30,         # Excellent composure
    },
    'nervous': {
        'shot_attempt': -0.25,     # Hesitant to shoot
        'long_shot': -0.35,        # Avoids difficult shots
        'shot_accuracy': -0.20,    # Nervousness affects accuracy
        'shot_power': -0.15,       # Tentative shots
        'composure': -0.35,        # Poor composure in key moments
    },
}

# =============================================================================
# DEFENDING MODIFIERS
# Influence on defensive actions and positioning
# =============================================================================

DEFENDING_MODIFIERS = {
    'aggressive': {
        'tackle_attempt': 0.30,    # More likely to go for tackles
        'interception': 0.20,      # Aggressive pressing
        'foul_tendency': 0.40,     # Higher chance of committing fouls
        'card_risk': 0.35,         # More likely to get booked
        'positioning': -0.10,      # May be out of position
        'pressing': 0.35,          # High pressing intensity
    },
    'cautious': {
        'tackle_attempt': -0.20,   # More careful tackling
        'interception': 0.25,      # Good at reading game
        'foul_tendency': -0.35,    # Much less likely to foul
        'card_risk': -0.40,        # Rarely gets cards
        'positioning': 0.25,       # Excellent positioning
        'pressing': -0.15,         # More controlled pressing
    },
    'creative': {
        'tackle_attempt': 0.05,    # Balanced approach
        'interception': 0.30,      # Reads game well
        'foul_tendency': -0.10,    # Smart defending
        'card_risk': -0.15,        # Intelligent defending
        'positioning': 0.20,       # Good positioning
        'pressing': 0.15,          # Smart pressing
    },
    'selfish': {
        'tackle_attempt': 0.15,    # Individual defending
        'interception': -0.10,     # Less team-oriented
        'foul_tendency': 0.20,     # May foul to stop play
        'card_risk': 0.25,         # Higher card risk
        'positioning': -0.15,      # May abandon position
        'pressing': 0.10,          # Individual pressing
    },
    'team_player': {
        'tackle_attempt': 0.10,    # Team-focused defending
        'interception': 0.25,      # Good team defending
        'foul_tendency': -0.15,    # Smart team defending
        'card_risk': -0.20,        # Disciplined
        'positioning': 0.30,       # Excellent team positioning
        'pressing': 0.25,          # Coordinated pressing
    },
    'confident': {
        'tackle_attempt': 0.20,    # Confident challenges
        'interception': 0.15,      # Backs judgment
        'foul_tendency': 0.10,     # May be overconfident
        'card_risk': 0.15,         # Slight increase in cards
        'positioning': 0.15,       # Confident positioning
        'pressing': 0.20,          # Confident pressing
    },
    'nervous': {
        'tackle_attempt': -0.25,   # Hesitant to tackle
        'interception': -0.15,     # Less decisive
        'foul_tendency': 0.15,     # Panic fouls
        'card_risk': 0.20,         # Cards from poor decisions
        'positioning': -0.25,      # Poor positioning
        'pressing': -0.20,         # Hesitant pressing
    },
}

# =============================================================================
# DECISION MODIFIERS
# Influence on general decision-making during play
# =============================================================================

DECISION_MODIFIERS = {
    'aggressive': {
        'risk_taking': 0.40,       # High risk decisions
        'decision_speed': 0.25,    # Quick decisions
        'option_evaluation': -0.15, # May not consider all options
        'pressure_handling': 0.10, # Thrives under pressure
        'leadership': 0.20,        # Natural leader
    },
    'cautious': {
        'risk_taking': -0.45,      # Very low risk decisions
        'decision_speed': -0.25,   # Slower decision making
        'option_evaluation': 0.30, # Considers all options
        'pressure_handling': -0.15, # Struggles under pressure
        'leadership': -0.10,       # Less assertive leader
    },
    'creative': {
        'risk_taking': 0.25,       # Creative risks
        'decision_speed': 0.20,    # Quick creative thinking
        'option_evaluation': 0.35, # Sees unique options
        'pressure_handling': 0.20, # Creative under pressure
        'leadership': 0.15,        # Inspirational leader
    },
    'selfish': {
        'risk_taking': 0.20,       # Personal risks
        'decision_speed': 0.15,    # Quick for personal gain
        'option_evaluation': -0.25, # Focuses on personal options
        'pressure_handling': -0.10, # Pressure affects judgment
        'leadership': -0.20,       # Poor team leadership
    },
    'team_player': {
        'risk_taking': 0.05,       # Balanced team risks
        'decision_speed': 0.10,    # Good team decisions
        'option_evaluation': 0.25, # Considers team options
        'pressure_handling': 0.25, # Team support helps
        'leadership': 0.30,        # Excellent team leader
    },
    'confident': {
        'risk_taking': 0.30,       # Confident risks
        'decision_speed': 0.25,    # Decisive
        'option_evaluation': 0.15, # Backs judgment
        'pressure_handling': 0.35, # Excellent under pressure
        'leadership': 0.40,        # Natural confident leader
    },
    'nervous': {
        'risk_taking': -0.35,      # Avoids risks
        'decision_speed': -0.30,   # Hesitant decisions
        'option_evaluation': -0.20, # Overthinks options
        'pressure_handling': -0.40, # Poor under pressure
        'leadership': -0.35,       # Lacks leadership confidence
    },
}

# =============================================================================
# SPECIAL SITUATIONS
# Modifiers for specific game situations
# =============================================================================

SPECIAL_SITUATIONS = {
    'penalty_kick': {
        'aggressive': {'accuracy': -0.10, 'power': 0.25, 'composure': -0.05},
        'cautious': {'accuracy': 0.20, 'power': -0.15, 'composure': 0.15},
        'creative': {'accuracy': 0.15, 'power': 0.10, 'composure': 0.25},
        'selfish': {'accuracy': 0.05, 'power': 0.20, 'composure': -0.10},
        'team_player': {'accuracy': 0.10, 'power': 0.05, 'composure': 0.20},
        'confident': {'accuracy': 0.25, 'power': 0.15, 'composure': 0.40},
        'nervous': {'accuracy': -0.30, 'power': -0.20, 'composure': -0.50},
    },
    'free_kick': {
        'aggressive': {'accuracy': -0.05, 'power': 0.30, 'creativity': 0.10},
        'cautious': {'accuracy': 0.15, 'power': -0.10, 'creativity': -0.15},
        'creative': {'accuracy': 0.25, 'power': 0.10, 'creativity': 0.45},
        'selfish': {'accuracy': 0.10, 'power': 0.25, 'creativity': 0.15},
        'team_player': {'accuracy': 0.15, 'power': 0.05, 'creativity': 0.20},
        'confident': {'accuracy': 0.20, 'power': 0.20, 'creativity': 0.30},
        'nervous': {'accuracy': -0.25, 'power': -0.15, 'creativity': -0.30},
    },
    'corner_kick': {
        'aggressive': {'accuracy': 0.05, 'power': 0.20, 'delivery': 0.10},
        'cautious': {'accuracy': 0.20, 'power': -0.05, 'delivery': 0.15},
        'creative': {'accuracy': 0.25, 'power': 0.10, 'delivery': 0.35},
        'selfish': {'accuracy': -0.10, 'power': 0.15, 'delivery': -0.15},
        'team_player': {'accuracy': 0.20, 'power': 0.05, 'delivery': 0.30},
        'confident': {'accuracy': 0.15, 'power': 0.15, 'delivery': 0.25},
        'nervous': {'accuracy': -0.20, 'power': -0.10, 'delivery': -0.25},
    },
    'one_on_one': {
        'aggressive': {'finishing': 0.15, 'composure': -0.10, 'decision': 0.20},
        'cautious': {'finishing': -0.05, 'composure': 0.25, 'decision': -0.15},
        'creative': {'finishing': 0.25, 'composure': 0.20, 'decision': 0.30},
        'selfish': {'finishing': 0.20, 'composure': -0.05, 'decision': 0.10},
        'team_player': {'finishing': 0.10, 'composure': 0.15, 'decision': 0.20},
        'confident': {'finishing': 0.30, 'composure': 0.40, 'decision': 0.35},
        'nervous': {'finishing': -0.25, 'composure': -0.45, 'decision': -0.30},
    },
    'last_minute': {
        'aggressive': {'urgency': 0.40, 'accuracy': -0.15, 'risk_taking': 0.50},
        'cautious': {'urgency': -0.20, 'accuracy': 0.10, 'risk_taking': -0.30},
        'creative': {'urgency': 0.25, 'accuracy': 0.15, 'risk_taking': 0.30},
        'selfish': {'urgency': 0.35, 'accuracy': -0.10, 'risk_taking': 0.40},
        'team_player': {'urgency': 0.30, 'accuracy': 0.05, 'risk_taking': 0.25},
        'confident': {'urgency': 0.35, 'accuracy': 0.20, 'risk_taking': 0.45},
        'nervous': {'urgency': -0.25, 'accuracy': -0.25, 'risk_taking': -0.40},
    },
}

# =============================================================================
# UTILITY FUNCTIONS
# Helper functions for accessing and validating modifiers
# =============================================================================

def get_modifier_by_trait(trait, action_type, category=None):
    """
    Get modifier value for a specific trait and action.
    
    Args:
        trait (str): Personality trait ('aggressive', 'cautious', etc.)
        action_type (str): Type of action ('forward_pass', 'shot_attempt', etc.)
        category (str, optional): Category to search in. If None, searches all categories.
    
    Returns:
        float: Modifier value, or 0.0 if not found
    
    Example:
        modifier = get_modifier_by_trait('aggressive', 'shot_attempt')
        # Returns 0.35
    """
    if category:
        categories = [globals().get(f'{category.upper()}_MODIFIERS', {})]
    else:
        categories = [PASSING_MODIFIERS, SHOOTING_MODIFIERS, DEFENDING_MODIFIERS, DECISION_MODIFIERS]
    
    for category_dict in categories:
        if trait in category_dict and action_type in category_dict[trait]:
            return category_dict[trait][action_type]
    
    return 0.0

def get_situation_modifiers(situation, trait):
    """
    Get modifiers for special situations.
    
    Args:
        situation (str): Special situation ('penalty_kick', 'free_kick', etc.)
        trait (str): Personality trait
    
    Returns:
        dict: Dictionary of modifiers for the situation, or empty dict if not found
    
    Example:
        modifiers = get_situation_modifiers('penalty_kick', 'confident')
        # Returns {'accuracy': 0.25, 'power': 0.15, 'composure': 0.40}
    """
    if situation in SPECIAL_SITUATIONS and trait in SPECIAL_SITUATIONS[situation]:
        return SPECIAL_SITUATIONS[situation][trait].copy()
    return {}

def get_all_modifiers_for_trait(trait):
    """
    Get all modifiers for a specific personality trait across all categories.
    
    Args:
        trait (str): Personality trait
    
    Returns:
        dict: Dictionary with categories as keys and modifier dicts as values
    
    Example:
        all_mods = get_all_modifiers_for_trait('aggressive')
        # Returns all aggressive modifiers organized by category
    """
    result = {}
    
    categories = {
        'passing': PASSING_MODIFIERS,
        'shooting': SHOOTING_MODIFIERS,
        'defending': DEFENDING_MODIFIERS,
        'decision': DECISION_MODIFIERS
    }
    
    for category_name, category_dict in categories.items():
        if trait in category_dict:
            result[category_name] = category_dict[trait].copy()
    
    # Add special situations
    special_mods = {}
    for situation, situation_dict in SPECIAL_SITUATIONS.items():
        if trait in situation_dict:
            special_mods[situation] = situation_dict[trait].copy()
    
    if special_mods:
        result['special_situations'] = special_mods
    
    return result

def validate_modifier_config():
    """
    Validate the modifier configuration for consistency and reasonable values.
    
    Returns:
        dict: Validation results with 'valid' boolean and 'issues' list
    
    Example:
        validation = validate_modifier_config()
        if not validation['valid']:
            print("Issues found:", validation['issues'])
    """
    issues = []
    
    # Define expected traits
    expected_traits = {'aggressive', 'cautious', 'creative', 'selfish', 'team_player', 'confident', 'nervous'}
    
    # Check each category
    categories = {
        'PASSING_MODIFIERS': PASSING_MODIFIERS,
        'SHOOTING_MODIFIERS': SHOOTING_MODIFIERS,
        'DEFENDING_MODIFIERS': DEFENDING_MODIFIERS,
        'DECISION_MODIFIERS': DECISION_MODIFIERS
    }
    
    for category_name, category_dict in categories.items():
        # Check if all expected traits are present
        missing_traits = expected_traits - set(category_dict.keys())
        if missing_traits:
            issues.append(f"{category_name}: Missing traits: {missing_traits}")
        
        # Check modifier values are reasonable (-0.5 to +0.5)
        for trait, modifiers in category_dict.items():
            for action, value in modifiers.items():
                if not isinstance(value, (int, float)):
                    issues.append(f"{category_name}.{trait}.{action}: Non-numeric value {value}")
                elif abs(value) > 0.5:
                    issues.append(f"{category_name}.{trait}.{action}: Extreme value {value} (should be -0.5 to +0.5)")
    
    # Check special situations
    for situation, situation_dict in SPECIAL_SITUATIONS.items():
        missing_traits = expected_traits - set(situation_dict.keys())
        if missing_traits:
            issues.append(f"SPECIAL_SITUATIONS.{situation}: Missing traits: {missing_traits}")
        
        for trait, modifiers in situation_dict.items():
            for modifier, value in modifiers.items():
                if not isinstance(value, (int, float)):
                    issues.append(f"SPECIAL_SITUATIONS.{situation}.{trait}.{modifier}: Non-numeric value {value}")
                elif abs(value) > 0.5:
                    issues.append(f"SPECIAL_SITUATIONS.{situation}.{trait}.{modifier}: Extreme value {value}")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }

def get_trait_impact_summary(trait):
    """
    Get a summary of how a personality trait impacts gameplay.
    
    Args:
        trait (str): Personality trait
    
    Returns:
        dict: Summary of trait impacts organized by area
    
    Example:
        summary = get_trait_impact_summary('aggressive')
        # Returns organized summary of aggressive trait impacts
    """
    all_mods = get_all_modifiers_for_trait(trait)
    
    summary = {
        'trait': trait,
        'strengths': [],
        'weaknesses': [],
        'neutral': []
    }
    
    # Analyze all modifiers
    for category, modifiers in all_mods.items():
        if category == 'special_situations':
            continue  # Handle separately
        
        for action, value in modifiers.items():
            impact_desc = f"{category}.{action}: {value:+.2f}"
            
            if value > 0.15:
                summary['strengths'].append(impact_desc)
            elif value < -0.15:
                summary['weaknesses'].append(impact_desc)
            else:
                summary['neutral'].append(impact_desc)
    
    return summary

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Available personality traits
AVAILABLE_TRAITS = ['aggressive', 'cautious', 'creative', 'selfish', 'team_player', 'confident', 'nervous']

# Modifier categories
MODIFIER_CATEGORIES = ['passing', 'shooting', 'defending', 'decision']

# Special situation types
SPECIAL_SITUATION_TYPES = ['penalty_kick', 'free_kick', 'corner_kick', 'one_on_one', 'last_minute']

# Validation ranges
MIN_MODIFIER_VALUE = -0.5
MAX_MODIFIER_VALUE = 0.5

if __name__ == "__main__":
    # Run validation when module is executed directly
    validation = validate_modifier_config()
    
    if validation['valid']:
        print("✓ Personality modifier configuration is valid")
        print(f"✓ {len(AVAILABLE_TRAITS)} personality traits configured")
        print(f"✓ {len(MODIFIER_CATEGORIES)} action categories defined")
        print(f"✓ {len(SPECIAL_SITUATION_TYPES)} special situations covered")
        
        # Show example usage
        print("\nExample usage:")
        print(f"Aggressive shot attempt modifier: {get_modifier_by_trait('aggressive', 'shot_attempt'):+.2f}")
        print(f"Confident penalty kick modifiers: {get_situation_modifiers('penalty_kick', 'confident')}")
        
    else:
        print("✗ Configuration validation failed:")
        for issue in validation['issues']:
            print(f"  - {issue}")