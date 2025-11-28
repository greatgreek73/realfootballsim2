#!/usr/bin/env python
"""
Diagnostic script for verifying Markov-based match simulation.
"""
import os
import sys
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.utils import timezone
from matches.models import Match, MatchEvent
from tournaments.tasks import simulate_active_matches, advance_match_minutes
from matches.engines.markov_runtime import simulate_markov_minute # Import to inspect directly
from players.models import Player

def debug_markov_match():
    print("=== DEBUGGING MARKOV MATCH SIMULATION ===\n")
    
    # 1. Find or create a test match
    # TARGET SPECIFIC MATCH IF NEEDED
    target_id = 4831
    match = Match.objects.filter(id=target_id).first()
    
    if not match:
        print(f"Match {target_id} not found, falling back to first active match.")
        matches = Match.objects.filter(status='in_progress')
        if not matches.exists():
            print("No matches in progress.")
            return
        match = matches.first()
        
    print(f"Using Match ID: {match.id}")
    print(f"  Home: {match.home_team.name}")
    print(f"  Away: {match.away_team.name}")
    print(f"  Status: {match.status}")
    print(f"  Current Minute: {match.current_minute}")

    # 2. Inspect Rosters extraction (simulating what happens in tasks.py)
    print("\n--- Roster Extraction Test ---")
    from players.models import get_player_line
    
    rosters_map = {"home": {}, "away": {}}

    def _build_team_roster(team_side, lineup_data):
        if not lineup_data: 
            print(f"  Warning: No lineup data for {team_side}")
            return
        pids = []
        for slot, p_info in lineup_data.items():
            if isinstance(p_info, dict):
                pid = p_info.get('playerId')
            else:
                pid = p_info
            
            if pid: pids.append(pid)
        
        if not pids: 
            print(f"  No players found for {team_side} in lineup structure")
            return

        players_qs = Player.objects.filter(id__in=pids)
        print(f"  Found {players_qs.count()} players for {team_side} (IDs: {pids})")
        
        for p in players_qs:
            line = get_player_line(p)
            stats = {"overall": p.overall_rating}
            player_entry = {
                "id": p.id,
                "name": p.last_name,
                "stats": stats,
            }
            if line not in rosters_map[team_side]:
                rosters_map[team_side][line] = []
            rosters_map[team_side][line].append(player_entry)
            
            # Print first player of each line as sample
            # if len(rosters_map[team_side][line]) == 1:
            #    print(f"    Added {p.last_name} to {team_side} {line}")

    _build_team_roster("home", match.home_lineup)
    _build_team_roster("away", match.away_lineup)

    if not rosters_map["home"] and not rosters_map["away"]:
        print("WARNING: Rosters are empty! Check if line-ups are set correctly on the match object.")
        print(f"Home Lineup Raw: {match.home_lineup}")
        print(f"Away Lineup Raw: {match.away_lineup}")
    
    # 3. Run a direct simulation step
    print("\n--- Direct Simulation Step (simulate_markov_minute) ---")
    try:
        seed_value = int(match.markov_seed or match.id) + int(time.time()) # mix in time for entropy in test
        print(f"  Running with seed: {seed_value}")
        result = simulate_markov_minute(
            seed=seed_value,
            token=match.markov_token,
            home_name=match.home_team.name,
            away_name=match.away_team.name,
            rosters=rosters_map,
        )
        
        summary = result['minute_summary']
        print(f"  Simulated Minute: {summary['minute']}")
        print(f"  Events Count: {len(summary['events'])}")
        
        actors_involved = set()
        for event in summary['events']:
            actor = event.get('actor_name')
            if actor:
                actors_involved.add(actor)
            
            # Print structured log
            desc = event.get('narrative') or "No narrative"
            print(f"    Tick {event.get('tick')}: {desc} [Actor: {actor}]")

        print(f"\n  Unique Actors involved this minute: {actors_involved}")
        print("SUCCESS: Simulation step completed without error.")
        
    except Exception as e:
        print(f"ERROR during simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_markov_match()
