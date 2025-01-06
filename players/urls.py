from django.urls import path
from .views import PlayerDetailView, boost_player
from . import views

urlpatterns = [
    path('detail/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),

    # Указываем просто '<int:player_id>/...', без 'players/'
    path('<int:player_id>/boost_player_ajax/', views.boost_player_ajax, name='player_boost_ajax'),

    path('boost/<int:player_id>/', boost_player, name='player_boost'),
]
