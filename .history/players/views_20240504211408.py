from django.views.generic import DetailView
from .models import Player

class PlayerDetailView(DetailView):
    model = Player
    template_name = 'players/player_detail.html'