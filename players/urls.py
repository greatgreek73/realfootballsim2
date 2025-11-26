from django.urls import path
from .views import PlayerDetailView, boost_player, delete_player, training_settings, update_training_settings
from . import views

app_name = 'players'

urlpatterns = [
    path('detail/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),
    
    # AJAX boost
    path('<int:player_id>/boost_player_ajax/', views.boost_player_ajax, name='player_boost_ajax'),
    
    # Обычная прокачка
    path('boost/<int:player_id>/', boost_player, name='player_boost'),
    
    # Маршрут для удаления игрока
    path('delete/<int:player_id>/', delete_player, name='player_delete'),
    
    # Настройки тренировок
    path('training/<int:player_id>/', training_settings, name='training_settings'),
    path('training/<int:player_id>/update/', update_training_settings, name='update_training_settings'),
]
