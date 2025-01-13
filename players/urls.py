from django.urls import path
from .views import PlayerDetailView, boost_player, delete_player
from . import views

urlpatterns = [
    path('detail/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),
    
    # AJAX boost
    path('<int:player_id>/boost_player_ajax/', views.boost_player_ajax, name='player_boost_ajax'),
    
    # Обычная прокачка
    path('boost/<int:player_id>/', boost_player, name='player_boost'),
    
    # Маршрут для удаления игрока
    path('delete/<int:player_id>/', delete_player, name='player_delete'),
]
