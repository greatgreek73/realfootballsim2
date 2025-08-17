# clubs/api_urls.py
from django.urls import path
from clubs.api_views import my_club, club_summary, club_players

urlpatterns = [
    path("my/club/", my_club, name="api-my-club"),
    path("clubs/<int:club_id>/summary/", club_summary, name="api-club-summary"),
    path("clubs/<int:club_id>/players/", club_players, name="api-club-players"),
]