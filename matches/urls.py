from django.urls import path
from . import views
from . import views_markov_demo
from . import views_markov_minute
from . import views_markov_ui

app_name = 'matches'

urlpatterns = [
    path('', views.MatchListView.as_view(), name='match_list'),
    path('create/', views.CreateMatchView.as_view(), name='create_match'),
    path('<int:pk>/', views.match_detail, name='match_detail'),  # Изменили на функцию
    path('championship/<int:championship_id>/matches/', views.MatchListView.as_view(), name='championship_matches'),
    path('<int:match_id>/events-json/', views.get_match_events, name='match_events_json'),
    path("markov-demo/", views_markov_demo.markov_demo, name="markov_demo"),
    path("markov-minute/", views_markov_minute.markov_minute, name="markov_minute"),
    path("markov-ui/", views_markov_ui.markov_ui, name="markov_ui"),
]
