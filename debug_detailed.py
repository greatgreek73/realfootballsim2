#!/usr/bin/env python
"""
Detailed debug to find the second error.
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

def debug_detailed():
    print("Detailed debugging...")
    
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
    
    # Setup string lineups (like real matches)
    players_home = list(home_club.player_set.all()[:11])
    players_away = list(away_club.player_set.all()[:11])
    
    match.home_lineup = ','.join([str(p.id) for p in players_home])
    match.away_lineup = ','.join([str(p.id) for p in players_away])
    match.save()
    
    print(f"Match setup complete: {match.id}")
    
    # Try multiple actions to find the error
    for i in range(5):
        try:
            print(f"Action {i+1}...")
            result = simulate_one_action(match)
            print(f"Result {i+1}: {result}")
            match.refresh_from_db()
        except Exception as e:
            print(f"ERROR on action {i+1}: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    debug_detailed()