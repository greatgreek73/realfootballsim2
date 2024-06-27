from django.urls import path
from . import views
from .views import CreateClubView, ClubDetailView

app_name = 'clubs'  # Добавляем пространство имен для приложения

urlpatterns = [
    path('create/', CreateClubView.as_view(), name='create_club'),
    path('detail/<int:pk>/', ClubDetailView.as_view(), name='club_detail'),
    path('detail/<int:pk>/create_player/', views.create_player, name='create_player'),
    
    # Новые пути для работы с составом команды
    path('detail/<int:pk>/team-selection/', views.team_selection_view, name='team_selection'),
    path('detail/<int:pk>/get-players/', views.get_players, name='get_players'),
    path('detail/<int:pk>/save-team-lineup/', views.save_team_lineup, name='save_team_lineup'),
    path('detail/<int:pk>/get-team-lineup/', views.get_team_lineup, name='get_team_lineup'),
]