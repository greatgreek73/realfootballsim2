import json
import random
import logging

from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, DetailView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from faker import Faker

from .models import Club
from .forms import ClubForm
from .country_locales import country_locales
from players.models import Player
from players.utils import generate_player_stats
from players.constants import PLAYER_PRICES
from tournaments.models import Championship, League

logger = logging.getLogger(__name__)

class CreateClubView(CreateView):
    """
    Представление для создания нового клуба.
    """
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

                # Generate initial 16 players for the new club
                self.generate_initial_players(club)

                if not club.id:
                    messages.error(
                        self.request,
                        "Error creating club: no ID received"
                    )
                    return self.form_invalid(form)

                messages.info(self.request, f"Club created with ID: {club.id}")

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
                            f'Club "{club.name}" created but not added to championship. Possibly no free spots.'
                        )

                return redirect('clubs:club_detail', pk=club.id)

        except Exception as e:
            logger.error(f'Error creating club: {str(e)}')
            messages.error(self.request, f'Error creating club: {str(e)}')
            return self.form_invalid(form)

    def generate_initial_players(self, club):
        """
        Генерирует начальный состав из 16 игроков.
        """
        positions = [
            {"position": "Goalkeeper",         "class": 4},
            {"position": "Right Back",         "class": 4},
            {"position": "Center Back",        "class": 4},
            {"position": "Center Back",        "class": 4},
            {"position": "Left Back",          "class": 4},
            {"position": "Left Midfielder",    "class": 4},
            {"position": "Central Midfielder", "class": 4},
            {"position": "Central Midfielder", "class": 4},
            {"position": "Right Midfielder",   "class": 4},
            {"position": "Center Forward",     "class": 4},
            {"position": "Center Forward",     "class": 4},

            # Запас (5)
            {"position": "Goalkeeper",         "class": 4},
            {"position": "Center Back",        "class": 4},
            {"position": "Central Midfielder", "class": 4},
            {"position": "Central Midfielder", "class": 4},
            {"position": "Center Forward",     "class": 4},
        ]

        country_code = club.country.code
        locale = get_locale_from_country_code(country_code)
        fake = Faker(locale)

        for player_info in positions:
            while True:
                first_name = fake.first_name_male()
                last_name = (
                    fake.last_name_male()
                    if hasattr(fake, 'last_name_male')
                    else fake.last_name()
                )
                if not Player.objects.filter(first_name=first_name, last_name=last_name).exists():
                    break

            stats = generate_player_stats(player_info["position"], player_info["class"])

            Player.objects.create(
                club=club,
                first_name=first_name,
                last_name=last_name,
                nationality=club.country,
                age=random.randint(18, 30),
                position=player_info["position"],
                player_class=player_info["class"],
                **stats
            )

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error creating club. Please check your input.'
        )
        return super().form_invalid(form)


class ClubDetailView(DetailView):
    """
    Детальная страница клуба.
    """
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
    return country_locales.get(country_code, 'en_US')


@require_http_methods(["GET"])
def create_player(request, pk):
    """
    Создаёт нового игрока в клубе (GET-параметры: position, player_class).
    """
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return HttpResponse("You don't have permission to create players in this club.", status=403)

    position = request.GET.get('position')
    player_class = int(request.GET.get('player_class', 1))

    cost = PLAYER_PRICES.get(player_class, 200)

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

        request.user.tokens -= cost
        request.user.save()

        messages.success(request, f'Successfully deducted {cost} tokens')
        messages.success(
            request,
            f'Player {player.first_name} {player.last_name} successfully created!'
        )
    except Exception as e:
        messages.error(request, f'Error creating player: {str(e)}')
        logger.error(f'Error creating player: {str(e)}')

    return redirect('clubs:club_detail', pk=pk)


@require_http_methods(["GET"])
def team_selection_view(request, pk):
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
    """
    Возвращает JSON со списком игроков клуба.
    **Здесь мы убрали stamina/defense/strength и добавили attack**
    """
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Access denied"}, status=403)

    players = Player.objects.filter(club=club)
    data = []
    for p in players:
        # Суммируем нужные характеристики: finishing, dribbling, accuracy, long_range, heading
        total_attack = (
            (p.finishing or 0) +
            (p.dribbling or 0) +
            (p.accuracy or 0) +
            (p.long_range or 0) +
            (p.heading or 0)
        )
        data.append({
            'id': p.id,
            'name': f"{p.first_name} {p.last_name}",
            'position': p.position,
            'playerClass': p.player_class,
            'attributes': {
                'attack': total_attack  # only one field in 'attributes' now
            }
        })
    return JsonResponse(data, safe=False)


@ensure_csrf_cookie
@require_http_methods(["POST"])
def save_team_lineup(request, pk):
    """
    Сохраняет состав (lineup).
    """
    try:
        club = get_object_or_404(Club, pk=pk)
        if club.owner != request.user:
            return JsonResponse({"error": "Access denied"}, status=403)

        data = json.loads(request.body)
        raw_lineup = data.get('lineup', {})
        tactic = data.get('tactic', 'balanced')

        logger.debug(f"save_team_lineup() received data: {data}")

        if len(raw_lineup) > 11:
            return JsonResponse({
                "success": False,
                "error": "Squad cannot have more than 11 players"
            }, status=400)

        has_goalkeeper = False

        from players.models import Player

        for slot_idx, slot_info in raw_lineup.items():
            if not isinstance(slot_info, dict):
                return JsonResponse({
                    "success": False,
                    "error": "Invalid format: each slot must be an object"
                }, status=400)

            p_id  = slot_info.get("playerId")
            p_pos = slot_info.get("playerPosition", "")

            try:
                p_obj = Player.objects.get(id=int(p_id))
            except Player.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "error": f"Player {p_id} does not exist"
                }, status=400)

            if p_obj.club_id != club.id:
                return JsonResponse({
                    "success": False,
                    "error": f"Player {p_id} does not belong to club {club.id}"
                }, status=400)

            if "goalkeeper" in p_pos.lower():
                has_goalkeeper = True

        if not has_goalkeeper:
            return JsonResponse({
                "success": False,
                "error": "Squad must include a goalkeeper"
            }, status=400)

        club.lineup = {
            "lineup": raw_lineup,
            "tactic": tactic
        }
        club.save()

        return JsonResponse({
            "success": True,
            "message": "Lineup and tactics saved successfully"
        })

    except json.JSONDecodeError:
        logger.error("JSONDecodeError: Cannot decode JSON from request body")
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error saving team lineup: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def get_team_lineup(request, pk):
    """
    Возвращает сохранённый состав.
    """
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Access denied"}, status=403)

    data = club.lineup or {}
    lineup_data = data.get('lineup', {})
    tactic = data.get('tactic', 'balanced')

    response = {
        'lineup': lineup_data,
        'tactic': tactic,
        'players': {}
    }

    from players.models import Player

    pids = []
    for info in lineup_data.values():
        if isinstance(info, dict):
            pid = info.get('playerId')
            if pid:
                pids.append(pid)

    if pids:
        qs = Player.objects.filter(id__in=pids)
        for pl in qs:
            response['players'][str(pl.id)] = {
                'name': f"{pl.first_name} {pl.last_name}",
                'position': pl.position,
                'playerClass': pl.player_class
            }

    return JsonResponse(response)

