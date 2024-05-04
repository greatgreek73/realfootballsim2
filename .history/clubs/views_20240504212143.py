# clubs/views.py
from django.views.generic import CreateView, DetailView
from django.shortcuts import redirect
from django.urls import reverse
from .models import Club
from .forms import ClubForm
from django.http import HttpResponseRedirect
from players.models import Player

class CreateClubView(CreateView):
    model = Club
    form_class = ClubForm
    template_name = 'clubs/create_club.html'

    def form_valid(self, form):
        club = form.save(commit=False)  # Сохраняем форму без коммита в базу данных
        club.owner = self.request.user  # Присваиваем текущего пользователя как владельца клуба
        club.save()  # Теперь сохраняем клуб в базу данных
        return redirect(reverse('clubs:club_detail', kwargs={'pk': club.pk}))  # Перенаправляем на страницу деталей клуба

class ClubDetailView(DetailView):
    model = Club
    template_name = 'clubs/club_detail.html'

def create_player(request, pk):
    club = Club.objects.get(pk=pk)
    player = Player.objects.create(club=club, nationality=club.country, age=17)
    return redirect(reverse('players:player_detail', args=[player.id]))