#!/usr/bin/env python
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from matches.models import Match, MatchEvent
from matches.match_simulation import MatchSimulation
from clubs.models import Club
from django.contrib.auth import get_user_model

User = get_user_model()

def test_simulate_one_action():
    """Test simulate_one_action and show full result with personality_reason"""
    print("\n=== TESTING simulate_one_action ===\n")
    
    # Get a match or create one
    try:
        match = Match.objects.filter(status='pending').first()
        if not match:
            # Create a test match
            club1 = Club.objects.first()
            club2 = Club.objects.exclude(id=club1.id).first()
            user = User.objects.first()
            
            match = Match.objects.create(
                home_club=club1,
                away_club=club2,
                championship=club1.championship,
                user=user,
                status='pending'
            )
            print(f"Created test match: {match.home_club.name} vs {match.away_club.name}")
        else:
            print(f"Using existing match: {match.home_club.name} vs {match.away_club.name}")
        
        # Initialize simulation
        simulation = MatchSimulation(match)
        simulation.setup_match()
        
        # Simulate one action
        print("\nSimulating one action...")
        result = simulation.simulate_one_action()
        
        # Show full result
        print("\n--- FULL RESULT FROM simulate_one_action ---")
        print(json.dumps(result, indent=2, default=str))
        
        # Check if personality_reason exists
        if 'personality_reason' in result:
            print(f"\n✓ personality_reason found: {result['personality_reason']}")
        else:
            print("\n✗ personality_reason NOT FOUND in result")
        
        return result, match
        
    except Exception as e:
        print(f"Error in simulate_one_action test: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def check_database_storage(match_id):
    """Check how personality_reason is stored in database"""
    print("\n\n=== CHECKING DATABASE STORAGE ===\n")
    
    try:
        # Get last few events for this match
        events = MatchEvent.objects.filter(match_id=match_id).order_by('-id')[:5]
        
        if not events:
            print("No events found for this match")
            return
        
        for i, event in enumerate(events):
            print(f"\n--- Event {i+1} (ID: {event.id}) ---")
            print(f"Event Type: {event.event_type}")
            print(f"Minute: {event.minute}")
            print(f"Player: {event.player.name if event.player else 'None'}")
            print(f"Description: {event.description[:100]}...")
            
            # Check personality_reason field
            if hasattr(event, 'personality_reason'):
                print(f"personality_reason field exists: {event.personality_reason}")
            else:
                print("personality_reason field does NOT exist on model")
            
            # Check in database directly
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT personality_reason FROM matches_matchevent WHERE id = %s",
                    [event.id]
                )
                row = cursor.fetchone()
                if row:
                    print(f"personality_reason in DB: {row[0]}")
                else:
                    print("No row found in DB")
                    
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()

def check_match_event_model():
    """Check MatchEvent model definition"""
    print("\n\n=== CHECKING MATCHEVENT MODEL ===\n")
    
    from matches.models import MatchEvent
    
    # List all fields
    print("MatchEvent fields:")
    for field in MatchEvent._meta.get_fields():
        print(f"  - {field.name} ({field.__class__.__name__})")
    
    # Check if personality_reason exists
    if hasattr(MatchEvent, 'personality_reason'):
        field = MatchEvent._meta.get_field('personality_reason')
        print(f"\n✓ personality_reason field exists")
        print(f"  Type: {field.__class__.__name__}")
        print(f"  Null: {field.null}")
        print(f"  Blank: {field.blank}")
    else:
        print("\n✗ personality_reason field NOT FOUND in model")

def main():
    # First check the model
    check_match_event_model()
    
    # Test simulate_one_action
    result, match = test_simulate_one_action()
    
    if match:
        # Check database storage
        check_database_storage(match.id)
    
    print("\n\n=== DEBUGGING COMPLETE ===")

if __name__ == "__main__":
    main()