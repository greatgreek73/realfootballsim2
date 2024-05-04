from django.urls import path
from .views import CreateClubView, ClubDetailView, CreatePlayerView

urlpatterns = [
    path('create/', CreateClubView.as_view(), name='create_club'),
    path('detail/<int:pk>/', ClubDetailView.as_view(), name='club_detail'),
    path('detail/<int:club_id>/create_player/', CreatePlayerView.as_view(), name='create_player'),
]
