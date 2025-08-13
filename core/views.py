from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tournaments.models import Championship

def home(request):
    """Home page view - shows welcome content for non-authenticated users,
    dashboard for authenticated users"""
    championships = Championship.objects.filter(status='in_progress').select_related('league')[:6]
    return render(request, 'core/home.html', {'championships': championships})

@login_required
def home_authenticated(request):
    """Protected home page - requires authentication"""
    championships = Championship.objects.filter(status='in_progress').select_related('league')[:6]
    return render(request, 'core/home.html', {'championships': championships})

@login_required  
def home_sub(request):
    """Protected sub-page - requires authentication"""
    return render(request, 'core/home_sub.html', {})