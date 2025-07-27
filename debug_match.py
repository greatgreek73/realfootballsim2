#!/usr/bin/env python
"""
Debug match simulation to find the personality traits issue.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.conf import settings
from matches.match_simulation import simulate_one_action
from matches.models import Match
from clubs.models import Club
from players.models import Player, get_player_line

def debug_simulate_action():
    print("Debugging simulate_one_action...")
    
    # Get two different clubs
    clubs_with_players = []
    for club in Club.objects.all():
        player_count = club.player_set.count()
        if player_count >= 15:
            clubs_with_players.append(club)
    
    if len(clubs_with_players) < 2:
        print("Not enough clubs with adequate players")
        return False
    
    home_club = clubs_with_players[0]
    away_club = clubs_with_players[1]
    
    print(f"Testing with {home_club.name} vs {away_club.name}")
    
    # Create a test match
    match = Match.objects.create(
        home_team=home_club,
        away_team=away_club,
        home_score=0,
        away_score=0,
        current_minute=1,
        status='in_progress'
    )
    
    # Setup basic lineups
    def setup_lineup(club, is_home):
        players = list(club.player_set.all()[:11])
        lineup_ids = [str(p.id) for p in players]
        if is_home:
            match.home_lineup = ','.join(lineup_ids)
        else:
            match.away_lineup = ','.join(lineup_ids)
    
    setup_lineup(home_club, True)
    setup_lineup(away_club, False)
    match.save()
    
    print(f"Match created: ID={match.id}")
    print(f"Home lineup: {match.home_lineup}")
    print(f"Away lineup: {match.away_lineup}")
    
    # Try to simulate one action
    try:
        print("Attempting to simulate one action...")
        result = simulate_one_action(match)
        print(f"Action result: {result}")
        return True
        
    except Exception as e:
        print(f"Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_simulate_action()
    if success:
        print("Debug completed successfully!")
    else:
        print("Debug failed!")