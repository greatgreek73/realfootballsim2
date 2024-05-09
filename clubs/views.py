# clubs/views.py
from django.views.generic import CreateView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import Club
from .forms import ClubForm
from players.models import Player
from django.http import HttpResponse
from faker import Faker

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
        # Передаем всех игроков, связанных с текущим клубом
        context['players'] = Player.objects.filter(club=self.object)
        return context

def create_player(request, pk):
    # Получаем объект клуба по его идентификатору или возвращаем 404-ошибку
    club = get_object_or_404(Club, pk=pk)

    # Инициализация Faker
    fake = Faker()

    # Получаем выбранную пользователем позицию из GET-параметров
    position = request.GET.get('position')

    # Проверяем, выбрал ли пользователь позицию
    if not position:
        return HttpResponse("Please select a position.")

    # Генерируем случайное имя и фамилию
    first_name = fake.first_name()
    last_name = fake.last_name()

    # Создаем нового игрока с случайным именем и фамилией, используя параметры клуба и выбранную позицию
    new_player = Player.objects.create(
        club=club,
        first_name=first_name,
        last_name=last_name,
        nationality=club.country,
        age=17,  # Вы можете изменить возраст по умолчанию
        position=position
    )

    # Перенаправляем на страницу с деталями нового игрока
    return redirect(reverse('players:player_detail', args=[new_player.id]))
