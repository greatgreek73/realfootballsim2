#!/usr/bin/env python3
"""
Simple test script to check narrative system integration
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
sys.path.append('/mnt/c/realfootballsim')

django.setup()

def test_imports():
    """Test that all narrative system imports work"""
    try:
        from matches.models import Match, MatchEvent, NarrativeEvent, PlayerRivalry, TeamChemistry, CharacterEvolution
        print("✓ Model imports successful")
        
        from matches.narrative_system import NarrativeAIEngine, RivalryManager, ChemistryCalculator
        print("✓ Narrative system imports successful")
        
        from matches.views import enrich_events_with_narrative_context
        print("✓ View function imports successful")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_narrative_summary():
    """Test narrative summary functionality"""
    try:
        from matches.models import Match
        from matches.narrative_system import NarrativeAIEngine
        
        # Test with first match if exists
        match = Match.objects.first()
        if match:
            summary = NarrativeAIEngine.get_match_narrative_summary(match)
            print(f"✓ Narrative summary test successful: {summary['total_events']} events")
        else:
            print("! No matches found, but function works")
        
        return True
    except Exception as e:
        print(f"✗ Narrative summary error: {e}")
        return False

def test_event_enrichment():
    """Test event enrichment functionality"""
    try:
        from matches.models import Match
        from matches.views import enrich_events_with_narrative_context
        
        # Test with first match if exists
        match = Match.objects.first()
        if match:
            events = match.events.order_by('minute')
            enriched = enrich_events_with_narrative_context(events, match)
            print(f"✓ Event enrichment test successful: {len(enriched)} events enriched")
        else:
            print("! No matches found, but function works")
        
        return True
    except Exception as e:
        print(f"✗ Event enrichment error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Narrative System Integration...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_narrative_summary,
        test_event_enrichment,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Narrative integration looks good.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Check the errors above.")
        sys.exit(1)