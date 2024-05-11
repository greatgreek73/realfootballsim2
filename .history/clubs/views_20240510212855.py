# clubs/views.py
from django.views.generic import CreateView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from faker import Faker
from .models import Club
from .forms import ClubForm
from players.models import Player

class CreateClubView(CreateView):
    model = Club
    form_class = ClubForm
    template_name = 'clubs/create_club.html'

    def form_valid(self, form):
        club = form.save(commit=False)
        club.owner = self.request.user
        club.save()
        return redirect(reverse('clubs:club_detail', kwargs={'pk': club.pk}))

class ClubDetailView(DetailView):
    model = Club
    template_name = 'clubs/club_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['players'] = Player.objects.filter(club=self.object)
        return context

def get_locale_from_country_code(country_code):
    """Привязывает код страны к локализации Faker."""
    country_locale_mapping = {
        'US': 'en_US',
        'FR': 'fr_FR',
        'DE': 'de_DE',
        'ES': 'es_ES',
        'IT': 'it_IT',
        'RU': 'ru_RU',
        # Добавьте другие сопоставления по мере необходимости
    }
    return country_locale_mapping.get(country_code, 'en_US')  # По умолчанию английский

def generate_unique_name(fake):
    """Генерирует уникальное сочетание мужского имени и фамилии."""
    while True:
        first_name = fake.first_name_male()
        last_name = fake.last_name()

        # Проверяем уникальность сочетания имени и фамилии
        if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
            return first_name, last_name

def create_player(request, pk):
    club = get_object_or_404(Club, pk=pk)

    # Получаем локализацию на основе страны клуба
    country_code = club.country.code
    locale = get_locale_from_country_code(country_code)

    # Инициализация Faker с соответствующей локализацией
    fake = Faker(locale)

    position = request.GET.get('position')

    if not position:
        return HttpResponse("Please select a position.")

    # Генерируем уникальное сочетание мужского имени и фамилии
    first_name, last_name = generate_unique_name(fake)

    new_player = Player.objects.create(
        club=club,
        first_name=first_name,
        last_name=last_name,
        nationality=club.country,
        age=17,
        position=position
    )

    return redirect(reverse('clubs:club_detail', args=[pk]))
