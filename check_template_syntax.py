#!/usr/bin/env python3
"""
Check Django template syntax for narrative integration
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')
sys.path.append('/mnt/c/realfootballsim')

django.setup()

def check_template_syntax():
    """Check if the template syntax is valid"""
    try:
        from django.template.loader import get_template
        from django.template import TemplateDoesNotExist, TemplateSyntaxError
        
        template_path = 'matches/match_detail.html'
        
        try:
            template = get_template(template_path)
            print(f"✓ Template '{template_path}' syntax is valid")
            return True
        except TemplateDoesNotExist:
            print(f"✗ Template '{template_path}' not found")
            return False
        except TemplateSyntaxError as e:
            print(f"✗ Template syntax error in '{template_path}': {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking template: {e}")
        return False

def check_css_file():
    """Check if CSS file exists and is accessible"""
    try:
        css_path = '/mnt/c/realfootballsim/matches/static/matches/css/match_detail.css'
        if os.path.exists(css_path):
            print(f"✓ CSS file exists: {css_path}")
            return True
        else:
            print(f"✗ CSS file not found: {css_path}")
            return False
    except Exception as e:
        print(f"✗ Error checking CSS file: {e}")
        return False

if __name__ == "__main__":
    print("Checking Template and CSS Integration...")
    print("=" * 50)
    
    tests = [
        check_template_syntax,
        check_css_file,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("✓ Template and CSS integration looks good!")
    else:
        print("✗ Some checks failed.")