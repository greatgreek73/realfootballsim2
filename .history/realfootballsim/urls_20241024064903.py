from django.contrib import admin
from django.urls import path, include
from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('', home, name='home'),
    path('core/', include('core.urls')),
    path('players/', include(('players.urls', 'players'), namespace='players')),
    path('clubs/', include(('clubs.urls', 'clubs'), namespace='clubs')),
    path('matches/', include(('matches.urls', 'matches'), namespace='matches')),  # Новая строка для приложения matches
    path('tournaments/', include('tournaments.urls', namespace='tournaments')),
]