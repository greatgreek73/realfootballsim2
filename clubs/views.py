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

class CreateClubView(CreateView):
    model = Club
    form_class = ClubForm
    template_name = 'clubs/create_club.html'

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # 1. Получаем данные из формы без сохранения
                club = form.save(commit=False)
                
                # 2. Установить владельца и другие поля
                club.owner = self.request.user
                club.is_bot = False
                club._skip_clean = True
                
                # 3. Найти подходящую лигу
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

                club.league = league
                
                # 4. Сохраняем клуб
                club.save()

                # 5. Проверяем ID сразу после сохранения
                if not club.id:
                    messages.error(self.request, "Ошибка при создании клуба: не получен ID")
                    return self.form_invalid(form)

                messages.info(self.request, f"Клуб создан с ID: {club.id}")
                
                # 6. Подождать немного, чтобы сигнал успел обработаться
                from time import sleep
                sleep(0.2)
                
                # 7. Проверить добавление в чемпионат
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
                    # Проверяем причину отсутствия в чемпионате
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

                # 8. Перенаправляем на страницу клуба
                return redirect('clubs:club_detail', pk=club.id)
                    
        except Exception as e:
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
    return country_locales.get(country_code, 'en_US')

@require_http_methods(["GET"])
def create_player(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return HttpResponse("У вас нет прав для создания игроков в этом клубе.", status=403)
    
    country_code = club.country.code
    locale = get_locale_from_country_code(country_code)
    fake = Faker(locale)

    position = request.GET.get('position')
    player_class = int(request.GET.get('player_class', 1))

    if not position:
        return HttpResponse("Пожалуйста, выберите позицию.")

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
    messages.success(request, f'Игрок {new_player.first_name} {new_player.last_name} успешно создан!')
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
    """Сохранение состава команды"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Доступ запрещен"}, status=403)
    
    try:
        lineup = json.loads(request.body)
        
        # Проверка корректности состава
        if len(lineup) > 11:
            return JsonResponse({
                "success": False,
                "error": "В составе не может быть больше 11 игроков"
            })

        # Проверка наличия вратаря
        goalkeeper_positions = [pos for pos, player_id in lineup.items() 
                              if Player.objects.get(id=player_id).position == 'Goalkeeper']
        if not goalkeeper_positions:
            return JsonResponse({
                "success": False,
                "error": "В составе должен быть вратарь"
            })

        # Сохранение состава
        club.lineup = lineup
        club.save()
        
        return JsonResponse({
            "success": True,
            "message": "Состав успешно сохранен"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Некорректный формат данных"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_team_lineup(request, pk):
    """Получение текущего состава команды"""
    club = get_object_or_404(Club, pk=pk)
    if club.owner != request.user:
        return JsonResponse({"error": "Доступ запрещен"}, status=403)
    
    lineup = club.lineup or {}
    
    # Добавляем дополнительную информацию об игроках в составе
    lineup_data = {
        'lineup': lineup,
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