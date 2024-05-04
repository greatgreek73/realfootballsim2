from django.views.generic import View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import Club
from players.models import Player, Position, Characteristic, PlayerCharacteristic

class CreatePlayerView(View):
    def post(self, request, club_id):
        position_id = request.POST.get('position')
        position = Position.objects.get(id=position_id)
        club = get_object_or_404(Club, pk=club_id)
        player = Player.objects.create(name=request.POST.get('name', 'New Player'), age=17, position=position, club=club)

        # Присваиваем характеристики игроку
        self.assign_characteristics(player)

        return redirect('clubs:club_detail', pk=club_id)

    def assign_characteristics(self, player):
        characteristics = Characteristic.objects.all()
        for characteristic in characteristics:
            PlayerCharacteristic.objects.create(
                player=player,
                characteristic=characteristic,
                value=characteristic.default_value
            )
