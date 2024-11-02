from django.views.generic import CreateView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from faker import Faker
from .models import Club
from .forms import ClubForm
from players.models import Player
from .country_locales import country_locales
from players.utils import generate_player_stats
import json
import logging

logger = logging.getLogger(__name__)

class CreateClubView(LoginRequiredMixin, CreateView):
    model = Club
    form_class = ClubForm
    template_name = 'clubs/create_club.html'

    def form_valid(self, form):
        logger.debug("CreateClubView form_valid called")
        logger.debug(f"Current user: {self.request.user.username}")
        
        try:
            logger.debug("Attempting to save form")
            club = form.save(commit=True, user=self.request.user)
            logger.debug(f"Club saved successfully with id: {club.pk}")
            
            return redirect(reverse('clubs:club_detail', kwargs={'pk': club.pk}))
        
        except Exception as e:
            logger.error(f"Error in form_valid: {str(e)}")
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.error("Form validation failed")
        logger.error(f"Form errors: {form.errors}")
        return super().form_invalid(form)
        
class ClubDetailView(LoginRequiredMixin, DetailView):
    model = Club
    template_name = 'clubs/club_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['players'] = Player.objects.filter(club=self.object)
        return context

def get_locale_from_country_code(country_code):
    return country_locales.get(country_code, 'en_US')

@login_required
def create_player(request, pk):
    club = get_object_or_404(Club, pk=pk)
    # Проверка, что пользователь является владельцем клуба
    if club.owner != request.user:
        return HttpResponse("You don't have permission to create players for this club.", status=403)
    
    country_code = club.country.code
    locale = get_locale_from_country_code(country_code)
    fake = Faker(locale)

    position = request.GET.get('position')
    player_class = int(request.GET.get('player_class', 1))

    if not position:
        return HttpResponse("Please select a position.")

    while True:
        first_name = fake.first_name_male()
        last_name = fake.last_name_male() if hasattr(fake, 'last_name_male') else fake.last_name()
        if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
            break

    stats = generate_player_stats(position, player_class)

    if position == 'Goalkeeper':
        new_player = Player.objects.create(
            club=club,
            first_name=first_name,
            last_name=last_name,
            nationality=club.country,
            age=17,
            position=position,
            player_class=player_class,
            strength=stats['strength'],
            stamina=stats['stamina'],
            pace=stats['pace'],
            positioning=stats['positioning'],
            reflexes=stats['reflexes'],
            handling=stats['handling'],
            aerial=stats['aerial'],
            jumping=stats['jumping'],
            command=stats['command'],
            throwing=stats['throwing'],
            kicking=stats['kicking']
        )
    else:
        new_player = Player.objects.create(
            club=club,
            first_name=first_name,
            last_name=last_name,
            nationality=club.country,
            age=17,
            position=position,
            player_class=player_class,
            strength=stats['strength'],
            stamina=stats['stamina'],
            pace=stats['pace'],
            marking=stats['marking'],
            tackling=stats['tackling'],
            work_rate=stats['work_rate'],
            positioning=stats['positioning'],
            passing=stats['passing'],
            crossing=stats['crossing'],
            dribbling=stats['dribbling'],
            ball_control=stats['ball_control'],
            heading=stats['heading'],
            finishing=stats['finishing'],
            long_range=stats['long_range'],
            vision=stats['vision']
        )

    new_player.save()
    return redirect(reverse('clubs:club_detail', args=[pk]))

@login_required
def team_selection_view(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return HttpResponse("You don't have permission to view this page.", status=403)
    return render(request, 'clubs/team_selection.html', {'club': club})

@login_required
@require_http_methods(["GET"])
def get_players(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Permission denied"}, status=403)
    players = Player.objects.filter(club=club)
    player_data = [{
        'id': player.id,
        'name': f"{player.first_name} {player.last_name}",
        'position': player.position
    } for player in players]
    return JsonResponse(player_data, safe=False)

@login_required
@require_http_methods(["POST"])
def save_team_lineup(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Permission denied"}, status=403)
    lineup = json.loads(request.body)
    club.lineup = lineup
    club.save()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["GET"])
def get_team_lineup(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Permission denied"}, status=403)
    lineup = club.lineup or {}
    return JsonResponse({'lineup': lineup})