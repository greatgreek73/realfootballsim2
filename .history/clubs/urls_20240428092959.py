# clubs/urls.py
from django.urls import path
from .views import CreateClubView, ClubDetailView

urlpatterns = [
    path('create/', CreateClubView.as_view(), name='create_club'),
    path('detail/', ClubDetailView.as_view(), name='club_detail'),
]
