#!/usr/bin/env python
"""
Simple diagnostic benchmark for PersonalityEngine.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.conf import settings
from matches.match_simulation import simulate_one_action
from matches.models import Match
from clubs.models import Club
from players.models import Player

def test_personality_engine():
    print("Testing PersonalityEngine integration...")
    
    # Get a club with players
    club = Club.objects.filter(player__isnull=False).first()
    if not club:
        print("No clubs with players found!")
        return
    
    print(f"Using club: {club.name}")
    
    # Get a player and check personality
    player = club.player_set.first()
    print(f"Player: {player.first_name} {player.last_name}")
    print(f"Personality traits: {player.personality_traits}")
    
    # Test PersonalityEngine imports
    try:
        from matches.personality_engine import PersonalityModifier, PersonalityDecisionEngine
        print("OK PersonalityEngine imports successful")
        
        # Test personality context
        context = {
            'possession_type': 'attack',
            'goal_distance': 20,
            'teammates_nearby': 2,
            'opponents_nearby': 1,
            'match_minute': 45,
            'pressure_level': 0.4,
            'score_difference': 0,
            'team_situation': 'drawing'
        }
        
        # Test decision engine
        action_type = PersonalityDecisionEngine.choose_action_type(player, context)
        risky = PersonalityDecisionEngine.should_attempt_risky_action(player, 0.6, context)
        
        print(f"OK Decision engine working: action={action_type}, risky={risky}")
        
    except Exception as e:
        print(f"ERROR PersonalityEngine error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_personality_engine()
    if success:
        print("OK PersonalityEngine test completed successfully!")
    else:
        print("ERROR PersonalityEngine test failed!")