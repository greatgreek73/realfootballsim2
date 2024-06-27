from . import views
from django.contrib import admin
from django.urls import path, include

app_name = 'clubs'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clubs/', include(('clubs.urls', 'clubs'), namespace='clubs')),
    path('create/', views.CreateClubView.as_view(), name='create_club'),
    path('detail/<int:pk>/', views.ClubDetailView.as_view(), name='club_detail'),
    path('detail/<int:pk>/create_player/', views.create_player, name='create_player'),
    path('detail/<int:pk>/team-selection/', views.team_selection_view, name='team_selection'),
    path('detail/<int:pk>/get-players/', views.get_players, name='get_players'),
    path('detail/<int:pk>/save-team-lineup/', views.save_team_lineup, name='save_team_lineup'),
    path('detail/<int:pk>/get-team-lineup/', views.get_team_lineup, name='get_team_lineup'),
]