from django.urls import path
from .views import PlayerDetailView, boost_player

urlpatterns = [
    path('detail/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),

    # Новый URL для «прокачки» игрока
    path('boost/<int:player_id>/', boost_player, name='player_boost'),
]
