from django.views.generic import CreateView, DetailView, View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import Club
from .forms import ClubForm
from players.models import Player, Position

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['positions'] = Position.objects.all()  # Добавляем список позиций в контекст
        return context

class CreatePlayerView(View):
    def post(self, request, club_id):
        position_id = request.POST.get('position')
        position = Position.objects.get(id=position_id)  # Используем ID для получения позиции
        club = get_object_or_404(Club, pk=club_id)
        Player.objects.create(name="New Player", age=20, position=position, club=club)
        return redirect('clubs:club_detail', pk=club_id)
