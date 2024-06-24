from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateMatchView.as_view(), name='create_match'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('<int:match_id>/simulate/', views.simulate_match_view, name='simulate_match'),
]