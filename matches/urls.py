from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.MatchListView.as_view(), name='match_list'),
    path('create/', views.CreateMatchView.as_view(), name='create_match'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('<int:match_id>/simulate/', views.simulate_match_view, name='simulate_match'),
    path('championship/<int:championship_id>/matches/', views.MatchListView.as_view(), name='championship_matches'),
    path('<int:match_id>/events-json/', views.get_match_events, name='match_events_json'),
]