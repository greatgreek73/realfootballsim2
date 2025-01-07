from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, DetailView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from faker import Faker
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Club
from players.models import Player
from tournaments.models import Championship, League
from players.utils import generate_player_stats
from .country_locales import country_locales
from .forms import ClubForm
from players.constants import PLAYER_PRICES
import json
import random
import logging

logger = logging.getLogger(__name__)

class CreateClubView(CreateView):
    model = Club
    form_class = ClubForm
    template_name = 'clubs/create_club.html'

    def form_valid(self, form):
        try:
            with transaction.atomic():
                club = form.save(commit=False)
                club.owner = self.request.user
                club.is_bot = False
                club._skip_clean = True

                league = League.objects.filter(
                    country=club.country,
                    level=1
                ).first()
                if not league:
                    messages.error(
                        self.request,
                        f'League not found for country {club.country.name}'
                    )
                    return self.form_invalid(form)

                club.league = league
                club.save()

                if not club.id:
                    messages.error(
                        self.request,
                        "Error creating club: no ID received"
                    )
                    return self.form_invalid(form)

                messages.info(self.request, f"Club created with ID: {club.id}")

                from time import sleep
                sleep(0.2)

                championship = Championship.objects.filter(
                    teams=club,
                    season__is_active=True
                ).first()
                if championship:
                    messages.success(
                        self.request,
                        f'Club "{club.name}" successfully created and added to {championship.league.name}!'
                    )
                else:
                    active_season = Championship.objects.filter(
                        season__is_active=True
                    ).exists()
                    if not active_season:
                        messages.warning(
                            self.request,
                            'No active season in the system.'
                        )
                    else:
                        messages.warning(
                            self.request,
                            f'Club "{club.name}" created but not added to championship. '
                            'Possibly no free spots.'
                        )

                return redirect('clubs:club_detail', pk=club.id)

        except Exception as e:
            logger.error(f'Error creating club: {str(e)}')
            messages.error(self.request, f'Error creating club: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error creating club. Please check your input.'
        )
        return super().form_invalid(form)

class ClubDetailView(DetailView):
    model = Club
    template_name = 'clubs/club_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['players'] = Player.objects.filter(club=self.object)
        context['player_prices'] = PLAYER_PRICES

        championship = Championship.objects.filter(
            teams=self.object,
            season__is_active=True
        ).first()
        context['championship'] = championship

        return context

def get_locale_from_country_code(country_code):
    """Returns locale for given country code."""
    return country_locales.get(country_code, 'en_US')

@require_http_methods(["GET"])
def create_player(request, pk):
    """Creates a new player for the club"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return HttpResponse("You don't have permission to create players in this club.", status=403)

    position = request.GET.get('position')
    player_class = int(request.GET.get('player_class', 1))
    
    # Get player cost
    cost = PLAYER_PRICES.get(player_class, 200)

    # Check balance
    if request.user.tokens < cost:
        messages.error(request, f'Insufficient tokens. Required: {cost}')
        return redirect('clubs:club_detail', pk=pk)

    if not position:
        return HttpResponse("Please select a position.")

    country_code = club.country.code
    locale = get_locale_from_country_code(country_code)
    fake = Faker(locale)

    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        first_name = fake.first_name_male()
        last_name = (
            fake.last_name_male()
            if hasattr(fake, 'last_name_male')
            else fake.last_name()
        )
        if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
            break
        attempts += 1

    if attempts >= max_attempts:
        messages.error(request, 'Failed to create unique name for player')
        return redirect('clubs:club_detail', pk=pk)

    try:
        stats = generate_player_stats(position, player_class)

        player = Player.objects.create(
            club=club,
            first_name=first_name,
            last_name=last_name,
            nationality=club.country,
            age=random.randint(17, 35),
            position=position,
            player_class=player_class,
            **stats
        )

        # Deduct tokens after successful player creation
        request.user.tokens -= cost
        request.user.save()
        messages.success(request, f'Successfully deducted {cost} tokens')
        messages.success(
            request,
            f'Player {player.first_name} {player.last_name} successfully created!'
        )
    except Exception as e:
        messages.error(
            request,
            f'Error creating player: {str(e)}'
        )
        logger.error(f'Error creating player: {str(e)}')

    return redirect('clubs:club_detail', pk=pk)

@require_http_methods(["GET"])
def team_selection_view(request, pk):
    """Team selection page view"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('clubs:club_detail', pk=pk)

    context = {
        'club': club,
        'current_section': 'team_selection'
    }
    return render(request, 'clubs/team_selection.html', context)

@require_http_methods(["GET"])
def get_players(request, pk):
    """Get club's player list"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Access denied"}, status=403)

    players = Player.objects.filter(club=club)
    player_data = [{
        'id': player.id,
        'name': f"{player.first_name} {player.last_name}",
        'position': player.position,
        'playerClass': player.player_class,
        'attributes': {
            'stamina': player.stamina,
            'strength': player.strength,
            'speed': player.pace
        }
    } for player in players]
    return JsonResponse(player_data, safe=False)

@ensure_csrf_cookie
@require_http_methods(["POST"])
def save_team_lineup(request, pk):
    """Save team lineup and tactics"""
    try:
        club = get_object_or_404(Club, pk=pk)
        if club.owner != request.user:
            return JsonResponse({"error": "Access denied"}, status=403)

        data = json.loads(request.body)
        lineup = data.get('lineup', {})
        tactic = data.get('tactic', 'balanced')

        if len(lineup) > 11:
            return JsonResponse({
                "success": False,
                "error": "Squad cannot have more than 11 players"
            })

        goalkeeper_positions = [
            pos for pos, player_id in lineup.items()
            if Player.objects.get(id=player_id).position == 'Goalkeeper'
        ]
        if not goalkeeper_positions:
            return JsonResponse({
                "success": False,
                "error": "Squad must include a goalkeeper"
            })

        club.lineup = {
            'lineup': lineup,
            'tactic': tactic
        }
        club.save()

        return JsonResponse({
            "success": True,
            "message": "Lineup and tactics saved successfully"
        })

    except json.JSONDecodeError:
        logger.error("JSONDecodeError: Cannot decode JSON from request body")
        return JsonResponse({
            "success": False,
            "error": "Invalid data format"
        }, status=400)
    except Exception as e:
        logger.error(f'Error saving team lineup: {str(e)}')
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_team_lineup(request, pk):
    """Get current team lineup and tactics"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Access denied"}, status=403)

    data = club.lineup or {}
    lineup = data.get('lineup', {})
    tactic = data.get('tactic', 'balanced')

    lineup_data = {
        'lineup': lineup,
        'tactic': tactic,
        'players': {}
    }

    if lineup:
        players = Player.objects.filter(id__in=lineup.values())
        lineup_data['players'] = {
            str(player.id): {
                'name': f"{player.first_name} {player.last_name}",
                'position': player.position,
                'playerClass': player.player_class
            } for player in players
        }

    return JsonResponse(lineup_data)