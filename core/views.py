from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'club'):
            return redirect('clubs:club_detail', pk=request.user.club.id)
        return redirect('clubs:create_club')
    return redirect('accounts:login')  # Исправлено: добавлен namespace