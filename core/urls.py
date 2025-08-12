from django.urls import path
from .views import home, home_authenticated, home_sub

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('home/', home_authenticated, name='home_authenticated'),
    path('home/sub/', home_sub, name='home_sub'),
]
