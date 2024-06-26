from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.MatchListView.as_view(), name='match_list'),
    path('create/', views.CreateMatchView.as_view(), name='create_match'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('<int:match_id>/simulate/', views.simulate_match_view, name='simulate_match'),
    path('team-selection/', views.team_selection_view, name='team_selection'),
    path('<int:match_id>/view-selection/', views.view_team_selection, name='view_team_selection'),
]