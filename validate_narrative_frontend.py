#!/usr/bin/env python3
"""
Simple validation script for narrative frontend integration (Level 1 MVP)
"""

import os
import re

def check_views_file():
    """Check that views.py has narrative enrichment function"""
    views_path = '/mnt/c/realfootballsim/matches/views.py'
    
    if not os.path.exists(views_path):
        print("✗ views.py not found")
        return False
        
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for essential narrative components
    checks = [
        ('enrich_events_with_narrative_context function', 'def enrich_events_with_narrative_context'),
        ('Rivalry check', 'RivalryManager.get_rivalry_between'),
        ('Chemistry check', 'ChemistryCalculator.get_chemistry_between'),
        ('Character evolution check', 'CharacterEvolution.objects.filter'),
        ('Narrative events check', 'NarrativeEvent.objects.filter'),
        ('Context enrichment', 'enriched_match_events'),
    ]
    
    passed = 0
    for check_name, pattern in checks:
        if pattern in content:
            print(f"✓ {check_name}")
            passed += 1
        else:
            print(f"✗ {check_name} - missing pattern: {pattern}")
    
    return passed == len(checks)

def check_template_file():
    """Check that template has narrative visualization elements"""
    template_path = '/mnt/c/realfootballsim/matches/templates/matches/match_detail.html'
    
    if not os.path.exists(template_path):
        print("✗ match_detail.html template not found")
        return False
        
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for narrative template elements
    checks = [
        ('Narrative event item styling', 'narrative-event-item'),
        ('Narrative importance classes', 'narrative-legendary'),
        ('Narrative indicators', 'narrative-indicators'),
        ('Rivalry icon', 'rivalry-icon'),
        ('Chemistry icon', 'chemistry-icon'),
        ('Growth icon', 'growth-icon'),
        ('Story icon', 'story-icon'),
        ('Narrative summary section', 'narrative-summary'),
        ('Bootstrap tooltips', 'data-bs-toggle="tooltip"'),
        ('Enriched events loop', 'enriched_match_events'),
    ]
    
    passed = 0
    for check_name, pattern in checks:
        if pattern in content:
            print(f"✓ {check_name}")
            passed += 1
        else:
            print(f"✗ {check_name} - missing pattern: {pattern}")
    
    return passed == len(checks)

def check_css_file():
    """Check that CSS has narrative styling"""
    css_path = '/mnt/c/realfootballsim/matches/static/matches/css/match_detail.css'
    
    if not os.path.exists(css_path):
        print("✗ match_detail.css not found")
        return False
        
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for narrative CSS classes
    checks = [
        ('Narrative event item style', '.narrative-event-item'),
        ('Legendary importance', '.narrative-legendary'),
        ('Major importance', '.narrative-major'),
        ('Significant importance', '.narrative-significant'),
        ('Minor importance', '.narrative-minor'),
        ('Narrative indicators', '.narrative-indicators'),
        ('Narrative icons', '.narrative-icon'),
        ('Rivalry icon style', '.rivalry-icon'),
        ('Chemistry icon style', '.chemistry-icon'),
        ('Growth icon style', '.growth-icon'),
        ('Story icon style', '.story-icon'),
        ('Narrative description', '.narrative-description'),
        ('Narrative summary', '.narrative-summary'),
    ]
    
    passed = 0
    for check_name, pattern in checks:
        if pattern in content:
            print(f"✓ {check_name}")
            passed += 1
        else:
            print(f"✗ {check_name} - missing pattern: {pattern}")
    
    return passed == len(checks)

def main():
    print("Validating Narrative Frontend Integration (Level 1 MVP)")
    print("=" * 60)
    
    tests = [
        ("Views.py Integration", check_views_file),
        ("Template Integration", check_template_file),
        ("CSS Styling", check_css_file),
    ]
    
    total_passed = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        if test_func():
            print(f"✓ {test_name} PASSED")
            total_passed += 1
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"Overall Result: {total_passed}/{total_tests} components validated")
    
    if total_passed == total_tests:
        print("✓ Level 1 MVP implementation appears complete!")
        print("✓ All narrative frontend integration components are in place")
        print("✓ Ready for testing with actual match data")
    else:
        print("✗ Some components are missing or incomplete")
        print("→ Review the failed checks above")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)