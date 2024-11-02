from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    path('', views.ChampionshipListView.as_view(), name='championship_list'),
    path('championship/<int:pk>/', views.ChampionshipDetailView.as_view(), name='championship_detail'),
    path('seasons/', views.SeasonListView.as_view(), name='season_list'),
    path('leagues/', views.LeagueListView.as_view(), name='league_list'),
]