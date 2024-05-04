from .views import create_player
from django.urls import path
from .views import CreateClubView, ClubDetailView

urlpatterns = [
    path('create/', CreateClubView.as_view(), name='create_club'),
    path('detail/<int:pk>/', ClubDetailView.as_view(), name='club_detail'),  # Добавлен параметр pk
    path('clubs/<int:club_id>/create_player/', create_player, name='create_player'),
]
