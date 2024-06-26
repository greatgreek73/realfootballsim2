from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.MatchListView.as_view(), name='match_list'),
    path('create/', views.CreateMatchView.as_view(), name='create_match'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('<int:match_id>/simulate/', views.simulate_match_view, name='simulate_match'),
    path('<int:match_id>/team-selection/', views.team_selection_view, name='team_selection'),
    path('<int:match_id>/get-players/', views.get_players, name='get_players'),
    path('<int:match_id>/save-team-selection/', views.save_team_selection, name='save_team_selection'),
    path('<int:match_id>/get-team-selection/', views.get_team_selection, name='get_team_selection'),
]