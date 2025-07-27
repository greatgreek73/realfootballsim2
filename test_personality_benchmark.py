#!/usr/bin/env python
"""
Benchmark script for testing Personality Engine performance and gameplay impact.

This script tests:
1. Performance impact of PersonalityEngine on match simulation speed
2. Gameplay differences in match statistics with/without PersonalityEngine

Usage:
    python test_personality_benchmark.py

Requirements:
    - Active clubs and players in the database
    - Django settings properly configured
"""

import os
import sys
import time
import json
import statistics
from datetime import datetime
from contextlib import contextmanager

# Setup Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
django.setup()

from django.conf import settings
from django.db import transaction
from matches.models import Match, MatchEvent
from clubs.models import Club
from players.models import Player
from matches.match_simulation import simulate_one_action


def simulate_match_instant(match):
    """Instantly simulate a complete match by running actions until completion."""
    match.status = 'in_progress'
    match.current_minute = 1
    match.save()
    
    max_actions = 1000  # Safety limit to prevent infinite loops
    action_count = 0
    
    while match.current_minute < 90 and action_count < max_actions:
        try:
            result = simulate_one_action(match)
            action_count += 1
            
            # If action completes an attack, advance minute
            if not result.get('continue', True):
                match.current_minute += 1
                match.save()
            
            match.refresh_from_db()
        except Exception as e:
            print(f"Error in action {action_count}: {e}")
            break
    
    # Finalize match
    match.status = 'finished'
    match.save()
    return match


@contextmanager
def temporary_setting(setting_name, value):
    """Context manager to temporarily change a Django setting."""
    original_value = getattr(settings, setting_name, None)
    setattr(settings, setting_name, value)
    try:
        yield
    finally:
        if original_value is not None:
            setattr(settings, setting_name, original_value)
        else:
            delattr(settings, setting_name)


class PersonalityBenchmark:
    """Benchmark class for testing PersonalityEngine performance and impact."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'performance': {},
            'gameplay': {}
        }
        
    def setup_test_match(self):
        """Create a test match between two clubs with adequate squads."""
        print("Setting up test match...")
        
        # Get clubs with enough players
        clubs_with_players = []
        for club in Club.objects.all():
            player_count = club.player_set.count()
            if player_count >= 15:  # Minimum squad size
                clubs_with_players.append((club, player_count))
        
        if len(clubs_with_players) < 2:
            raise Exception("Need at least 2 clubs with 15+ players each")
        
        # Sort by player count and pick the two most balanced clubs
        clubs_with_players.sort(key=lambda x: x[1])
        home_club = clubs_with_players[0][0]
        away_club = clubs_with_players[1][0]
        
        # Make sure we have different clubs
        home_index = 0
        away_index = 1
        for i, (club, count) in enumerate(clubs_with_players):
            if club.id != home_club.id:
                away_club = club
                away_index = i
                break
        
        print(f"Selected clubs: {home_club.name} ({clubs_with_players[home_index][1]} players) vs {away_club.name} ({clubs_with_players[away_index][1]} players)")
        return home_club, away_club
    
    def create_match(self, home_club, away_club):
        """Create a new match for testing."""
        # Clean up any existing test matches
        Match.objects.filter(
            home_team=home_club,
            away_team=away_club
        ).delete()
        
        match = Match.objects.create(
            home_team=home_club,
            away_team=away_club,
            home_score=0,
            away_score=0,
            current_minute=1,
            status='scheduled'
        )
        
        # Setup lineups automatically
        self.setup_basic_lineup(match, home_club, True)
        self.setup_basic_lineup(match, away_club, False)
        
        return match
    
    def setup_basic_lineup(self, match, club, is_home):
        """Setup a basic 4-4-2 formation for a team."""
        # Get 11 players for the lineup
        players = list(club.player_set.all()[:11])
        
        if len(players) < 11:
            print(f"Warning: {club.name} has only {len(players)} players, need 11")
            return
        
        # Create lineup dict in the format expected by the simulation
        lineup_dict = {}
        for i, player in enumerate(players):
            lineup_dict[str(i)] = str(player.id)
        
        # Set the lineup in the correct format
        if is_home:
            match.home_lineup = lineup_dict
        else:
            match.away_lineup = lineup_dict
        
        match.save()
    
    def run_performance_test(self, iterations=3):
        """Test performance impact of PersonalityEngine."""
        print("\\n" + "="*60)
        print("PERFORMANCE BENCHMARK")
        print("="*60)
        
        home_club, away_club = self.setup_test_match()
        
        # Test without PersonalityEngine
        print(f"\\nTesting {iterations} matches WITHOUT PersonalityEngine...")
        times_without = []
        
        for i in range(iterations):
            match = self.create_match(home_club, away_club)
            
            with temporary_setting('USE_PERSONALITY_ENGINE', False):
                start_time = time.time()
                simulate_match_instant(match)
                end_time = time.time()
                
            duration = end_time - start_time
            times_without.append(duration)
            print(f"  Match {i+1}: {duration:.3f}s")
        
        # Test with PersonalityEngine
        print(f"\\nTesting {iterations} matches WITH PersonalityEngine...")
        times_with = []
        
        for i in range(iterations):
            match = self.create_match(home_club, away_club)
            
            with temporary_setting('USE_PERSONALITY_ENGINE', True):
                start_time = time.time()
                simulate_match_instant(match)
                end_time = time.time()
                
            duration = end_time - start_time
            times_with.append(duration)
            print(f"  Match {i+1}: {duration:.3f}s")
        
        # Calculate performance impact
        avg_without = statistics.mean(times_without)
        avg_with = statistics.mean(times_with)
        performance_impact = ((avg_with - avg_without) / avg_without) * 100
        
        self.results['performance'] = {
            'iterations': iterations,
            'avg_time_without_personality': round(avg_without, 3),
            'avg_time_with_personality': round(avg_with, 3),
            'performance_impact_percent': round(performance_impact, 2),
            'all_times_without': [round(t, 3) for t in times_without],
            'all_times_with': [round(t, 3) for t in times_with]
        }
        
        print(f"\\nPERFORMANCE RESULTS:")
        print(f"  Average time WITHOUT PersonalityEngine: {avg_without:.3f}s")
        print(f"  Average time WITH PersonalityEngine: {avg_with:.3f}s")
        print(f"  Performance impact: {performance_impact:+.2f}%")
        
        return performance_impact
    
    def run_gameplay_test(self, iterations=5):
        """Test gameplay differences with/without PersonalityEngine."""
        print("\\n" + "="*60)
        print("GAMEPLAY IMPACT BENCHMARK")
        print("="*60)
        
        home_club, away_club = self.setup_test_match()
        
        # Collect statistics without PersonalityEngine
        print(f"\\nTesting {iterations} matches WITHOUT PersonalityEngine...")
        stats_without = []
        
        for i in range(iterations):
            match = self.create_match(home_club, away_club)
            
            with temporary_setting('USE_PERSONALITY_ENGINE', False):
                simulate_match_instant(match)
                
            match.refresh_from_db()
            stats = {
                'goals_home': match.home_score,
                'goals_away': match.away_score,
                'total_goals': match.home_score + match.away_score,
                'shots': match.st_shoots,
                'passes': match.st_passes,
                'possessions': match.st_possessions,
                'fouls': match.st_fouls
            }
            stats_without.append(stats)
            print(f"  Match {i+1}: {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name} | Shots: {match.st_shoots}, Passes: {match.st_passes}, Fouls: {match.st_fouls}")
        
        # Collect statistics with PersonalityEngine
        print(f"\\nTesting {iterations} matches WITH PersonalityEngine...")
        stats_with = []
        
        for i in range(iterations):
            match = self.create_match(home_club, away_club)
            
            with temporary_setting('USE_PERSONALITY_ENGINE', True):
                simulate_match_instant(match)
                
            match.refresh_from_db()
            stats = {
                'goals_home': match.home_score,
                'goals_away': match.away_score,
                'total_goals': match.home_score + match.away_score,
                'shots': match.st_shoots,
                'passes': match.st_passes,
                'possessions': match.st_possessions,
                'fouls': match.st_fouls
            }
            stats_with.append(stats)
            print(f"  Match {i+1}: {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name} | Shots: {match.st_shoots}, Passes: {match.st_passes}, Fouls: {match.st_fouls}")
        
        # Calculate averages and differences
        def calculate_averages(stats_list):
            if not stats_list:
                return {}
            
            keys = stats_list[0].keys()
            averages = {}
            for key in keys:
                values = [stat[key] for stat in stats_list]
                averages[key] = round(statistics.mean(values), 2)
            return averages
        
        avg_without = calculate_averages(stats_without)
        avg_with = calculate_averages(stats_with)
        
        # Calculate percentage differences
        differences = {}
        for key in avg_without.keys():
            if avg_without[key] > 0:
                diff_percent = ((avg_with[key] - avg_without[key]) / avg_without[key]) * 100
                differences[key] = round(diff_percent, 2)
            else:
                differences[key] = 0.0
        
        self.results['gameplay'] = {
            'iterations': iterations,
            'averages_without_personality': avg_without,
            'averages_with_personality': avg_with,
            'percentage_differences': differences,
            'raw_data_without': stats_without,
            'raw_data_with': stats_with
        }
        
        print(f"\\nGAMEPLAY RESULTS:")
        print(f"  Average statistics WITHOUT PersonalityEngine:")
        for key, value in avg_without.items():
            print(f"    {key}: {value}")
        
        print(f"\\n  Average statistics WITH PersonalityEngine:")
        for key, value in avg_with.items():
            print(f"    {key}: {value}")
        
        print(f"\\n  Percentage changes WITH PersonalityEngine:")
        for key, value in differences.items():
            print(f"    {key}: {value:+.2f}%")
        
        return differences
    
    def save_results(self, filename="personality_benchmark_results.json"):
        """Save benchmark results to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\\nResults saved to {filename}")
    
    def run_full_benchmark(self):
        """Run complete benchmark suite."""
        print("PERSONALITY ENGINE BENCHMARK SUITE")
        print("=" * 60)
        print("Testing PersonalityEngine performance and gameplay impact...")
        
        try:
            # Run performance test
            performance_impact = self.run_performance_test(iterations=3)
            
            # Run gameplay test  
            gameplay_differences = self.run_gameplay_test(iterations=5)
            
            # Summary
            print("\\n" + "="*60)
            print("BENCHMARK SUMMARY")
            print("="*60)
            print(f"Performance Impact: {performance_impact:+.2f}%")
            print("Key Gameplay Changes:")
            for stat, change in gameplay_differences.items():
                if abs(change) > 5:  # Only show significant changes
                    print(f"  {stat}: {change:+.2f}%")
            
            # Save results
            self.save_results()
            
            return True
            
        except Exception as e:
            print(f"\\nBenchmark failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    benchmark = PersonalityBenchmark()
    success = benchmark.run_full_benchmark()
    
    if success:
        print("\\nBenchmark completed successfully!")
    else:
        print("\\nBenchmark failed!")
        sys.exit(1)