from django.urls import path
from .views import PlayerDetailView

urlpatterns = [
    path('detail/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),
]