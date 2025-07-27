from django.urls import path
from . import views

app_name = 'narrative'

urlpatterns = [
    path('', views.StoryCenterView.as_view(), name='story_center'),
]