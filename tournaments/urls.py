from django.urls import path
from . import views, views_api

app_name = 'tournaments'

urlpatterns = [
    path('api/championships/', views_api.championship_list, name='api_championship_list'),
    path('api/championships/<int:pk>/', views_api.championship_detail, name='api_championship_detail'),
    path('api/championships/<int:pk>/matches/', views_api.championship_matches, name='api_championship_matches'),
    path('api/championships/my/', views_api.my_championship, name='api_my_championship'),
    path('api/seasons/', views_api.season_list, name='api_season_list'),
    path('api/leagues/', views_api.league_list, name='api_league_list'),
    path('', views.ChampionshipListView.as_view(), name='championship_list'),
    path('championship/<int:pk>/', views.ChampionshipDetailView.as_view(), name='championship_detail'),
    path('championship/<int:pk>/calendar/', views.ChampionshipCalendarView.as_view(), name='championship_calendar'),
    path('seasons/', views.SeasonListView.as_view(), name='season_list'),
    path('leagues/', views.LeagueListView.as_view(), name='league_list'),
    path('set-timezone/', views.set_timezone, name='set_timezone'),
    path('api/matches/<int:pk>/', views.get_championship_matches, name='api_matches'),
    path('my-championship/', views.MyChampionshipView.as_view(), name='my_championship'),
]
