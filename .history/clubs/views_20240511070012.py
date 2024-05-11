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
    # Просто формируем строку локали из кода страны
    return f"{country_code.lower()}_{country_code.upper()}"

def create_player(request, pk):
    club = get_object_or_404(Club, pk=pk)
    country_code = club.country.code
    locale = get_locale_from_country_code(country_code)
    fake = Faker(locale)

    position = request.GET.get('position')
    if not position:
        return HttpResponse("Please select a position.")

    unique = False
    while not unique:
        first_name = fake.first_name_male()
        last_name = fake.last_name()
        if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
            unique = True

    new_player = Player.objects.create(
        club=club,
        first_name=first_name,
        last_name=last_name,
        nationality=club.country,
        age=17,  # Возраст по умолчанию
        position=position
    )

    return redirect(reverse('clubs:club_detail', args=[pk]))
