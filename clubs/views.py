from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import CreateView, DetailView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from faker import Faker

from .models import Club
from players.models import Player
from tournaments.models import Championship, League
from players.utils import generate_player_stats
from .country_locales import country_locales
from .forms import ClubForm

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
                # 1. Получаем данные из формы без сохранения
                club = form.save(commit=False)
                club.owner = self.request.user
                club.is_bot = False
                club._skip_clean = True

                # 2. Найти подходящую лигу
                league = League.objects.filter(
                    country=club.country,
                    level=1
                ).first()
                if not league:
                    messages.error(
                        self.request,
                        f'Не найдена лига для страны {club.country.name}'
                    )
                    return self.form_invalid(form)

                # 3. Сохраняем клуб
                club.league = league
                club.save()

                # 4. Проверяем ID сразу после сохранения
                if not club.id:
                    messages.error(
                        self.request,
                        "Ошибка при создании клуба: не получен ID"
                    )
                    return self.form_invalid(form)

                messages.info(self.request, f"Клуб создан с ID: {club.id}")

                # 5. Ждём немного, чтобы сигнал успел обработаться
                from time import sleep
                sleep(0.2)

                # 6. Проверить добавление в чемпионат
                championship = Championship.objects.filter(
                    teams=club,
                    season__is_active=True
                ).first()
                if championship:
                    messages.success(
                        self.request,
                        f'Клуб "{club.name}" успешно создан и добавлен в {championship.league.name}!'
                    )
                else:
                    active_season = Championship.objects.filter(
                        season__is_active=True
                    ).exists()
                    if not active_season:
                        messages.warning(
                            self.request,
                            'Нет активного сезона в системе.'
                        )
                    else:
                        messages.warning(
                            self.request,
                            f'Клуб "{club.name}" создан, но не добавлен в чемпионат. '
                            'Возможно, нет свободных мест.'
                        )

                # 7. Перенаправляем на страницу клуба
                return redirect('clubs:club_detail', pk=club.id)

        except Exception as e:
            logger.error(f'Error creating club: {str(e)}')
            messages.error(self.request, f'Ошибка при создании клуба: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Ошибка при создании клуба. Проверьте введенные данные.'
        )
        return super().form_invalid(form)

class ClubDetailView(DetailView):
    model = Club
    template_name = 'clubs/club_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['players'] = Player.objects.filter(club=self.object)

        championship = Championship.objects.filter(
            teams=self.object,
            season__is_active=True
        ).first()
        context['championship'] = championship

        return context

def get_locale_from_country_code(country_code):
    """Возвращает локаль для заданного кода страны."""
    return country_locales.get(country_code, 'en_US')

@require_http_methods(["GET"])
def create_player(request, pk):
    """Создает нового игрока для клуба"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return HttpResponse("У вас нет прав для создания игроков в этом клубе.", status=403)

    position = request.GET.get('position')
    player_class = int(request.GET.get('player_class', 1))

    if not position:
        return HttpResponse("Пожалуйста, выберите позицию.")

    country_code = club.country.code
    locale = get_locale_from_country_code(country_code)
    fake = Faker(locale)

    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        first_name = fake.first_name_male()
        last_name = (fake.last_name_male()
                     if hasattr(fake, 'last_name_male')
                     else fake.last_name())
        # Проверяем, чтобы имя и фамилия были уникальными:
        if not Player.objects.filter(first_name=first_name,
                                     last_name=last_name).exists():
            break
        attempts += 1

    if attempts >= max_attempts:
        messages.error(request, 'Не удалось создать уникальное имя для игрока')
        return redirect('clubs:club_detail', pk=pk)

    try:
        # Генерируем статы игрока на основе позиции и класса
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

        messages.success(
            request,
            f'Игрок {player.first_name} {player.last_name} успешно создан!'
        )
    except Exception as e:
        messages.error(
            request,
            f'Ошибка при создании игрока: {str(e)}'
        )
        logger.error(f'Error creating player: {str(e)}')

    return redirect('clubs:club_detail', pk=pk)

@require_http_methods(["GET"])
def team_selection_view(request, pk):
    """Отображение страницы выбора состава"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        messages.error(request, "У вас нет прав для просмотра этой страницы.")
        return redirect('clubs:club_detail', pk=pk)

    context = {
        'club': club,
        'current_section': 'team_selection'
    }
    return render(request, 'clubs/team_selection.html', context)

@require_http_methods(["GET"])
def get_players(request, pk):
    """Получение списка игроков клуба"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Доступ запрещен"}, status=403)

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

@require_http_methods(["POST"])
def save_team_lineup(request, pk):
    """Сохранение состава команды и тактики (lineup и tactic)"""
    # Расширенное логирование для отладки
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Content-Type: {request.headers.get('Content-Type')}")
    logger.debug(f"CSRF Token in header: {request.headers.get('X-CSRFToken')}")
    logger.debug(f"CSRF Token in cookies: {request.COOKIES.get('csrftoken')}")
    logger.debug(f"Session cookie: {request.COOKIES.get('sessionid')}")

    club = get_object_or_404(Club, pk=pk)

    logger.debug(f"Club owner: {club.owner}, Request user: {request.user}, CSRF OK: {request.csrf_processing_done}")

    if club.owner != request.user:
        logger.debug("User is not the owner of the club. Returning 403 Forbidden.")
        return JsonResponse({"error": "Доступ запрещен"}, status=403)

    try:
        logger.debug(f"Request body (raw): {request.body}")
        data = json.loads(request.body)

        lineup = data.get('lineup', {})
        tactic = data.get('tactic', 'balanced')

        if len(lineup) > 11:
            return JsonResponse({
                "success": False,
                "error": "В составе не может быть больше 11 игроков"
            })

        # Проверка наличия вратаря
        goalkeeper_positions = [
            pos for pos, player_id in lineup.items()
            if Player.objects.get(id=player_id).position == 'Goalkeeper'
        ]
        if not goalkeeper_positions:
            return JsonResponse({
                "success": False,
                "error": "В составе должен быть вратарь"
            })

        # Сохраняем состав и тактику в клуб (club.lineup — JSONField или TextField)
        club.lineup = {
            'lineup': lineup,
            'tactic': tactic
        }
        club.save()

        return JsonResponse({
            "success": True,
            "message": "Состав и тактика успешно сохранены"
        })

    except json.JSONDecodeError:
        logger.error("JSONDecodeError: Невозможно декодировать JSON из тела запроса")
        return JsonResponse({
            "success": False,
            "error": "Некорректный формат данных"
        }, status=400)
    except Exception as e:
        logger.error(f'Error saving team lineup: {str(e)}')
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_team_lineup(request, pk):
    """Получение текущего состава команды и тактики"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Доступ запрещен"}, status=403)

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
