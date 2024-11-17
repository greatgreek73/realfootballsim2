from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    path('', views.ChampionshipListView.as_view(), name='championship_list'),
    path('championship/<int:pk>/', views.ChampionshipDetailView.as_view(), name='championship_detail'),
    path('championship/<int:pk>/calendar/', views.ChampionshipCalendarView.as_view(), name='championship_calendar'),
    path('seasons/', views.SeasonListView.as_view(), name='season_list'),
    path('leagues/', views.LeagueListView.as_view(), name='league_list'),
    path('set-timezone/', views.set_timezone, name='set_timezone'),
    path('api/matches/<int:pk>/', views.get_championship_matches, name='api_matches'),
    path('my-championship/', views.MyChampionshipView.as_view(), name='my_championship'),
]