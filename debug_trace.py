#!/usr/bin/env python
"""
Debug with tracing to find where simulate_one_action gets lost.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.conf import settings
from matches.models import Match
from clubs.models import Club

def debug_with_trace():
    print("Debug with trace...")
    
    # Get clubs
    clubs_with_players = []
    for club in Club.objects.all():
        player_count = club.player_set.count()
        if player_count >= 15:
            clubs_with_players.append(club)
    
    home_club = clubs_with_players[0]
    away_club = clubs_with_players[1]
    
    # Create a test match
    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        home_score=0,
        away_score=0,
        current_minute=1,
        status='in_progress'
    )
    
    # Setup string lineups
    players_home = list(home_club.player_set.all()[:11])
    players_away = list(away_club.player_set.all()[:11])
    
    match.home_lineup = ','.join([str(p.id) for p in players_home])
    match.away_lineup = ','.join([str(p.id) for p in players_away])
    match.save()
    
    print(f"Match: {home_club.name} vs {away_club.name}")
    print(f"current_player_with_ball: {match.current_player_with_ball}")
    print(f"current_zone: {match.current_zone}")
    
    # Import the function with potential patch for debugging
    from matches.match_simulation import simulate_one_action
    
    try:
        result = simulate_one_action(match)
        print(f"Final result: {result}")
        print(f"Result type: {type(result)}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_with_trace()