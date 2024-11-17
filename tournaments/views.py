from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import json
from django.utils import timezone
from django.http import JsonResponse
from django.db import models
from .models import Championship, Season, League

class ChampionshipListView(LoginRequiredMixin, ListView):
    model = Championship
    template_name = 'tournaments/championship_list.html'
    context_object_name = 'championships'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_seasons'] = Season.objects.filter(is_active=True)
        context['championships'] = Championship.objects.all().select_related(
            'league', 'season'
        ).order_by('league__level')
        return context

class ChampionshipDetailView(LoginRequiredMixin, DetailView):
    model = Championship
    template_name = 'tournaments/championship_detail.html'
    context_object_name = 'championship'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['standings'] = (
            self.object.championshipteam_set
            .annotate(
                goals_diff=models.F('goals_for') - models.F('goals_against')
            )
            .order_by('-points', '-goals_diff', '-goals_for')
        )
        
        matches = self.object.championshipmatch_set.all().select_related(
            'match', 
            'match__home_team', 
            'match__away_team'
        ).order_by('round', 'match__date')
        
        context['matches'] = matches
        
        calendar_events = []
        for match in matches:
            calendar_events.append({
                'id': match.id,
                'title': f"{match.match.home_team} vs {match.match.away_team}",
                'start': match.match.date.isoformat(),
                'status': match.match.status,
                'score': f"{match.match.home_score} - {match.match.away_score}" if match.match.status == 'finished' else None,
                'url': reverse('matches:match_detail', args=[match.match.id]),
                'className': f"match-{match.match.status}"
            })
        
        context['calendar_events'] = json.dumps(calendar_events)
        context['user_timezone'] = self.request.session.get('timezone', timezone.get_current_timezone_name())
        
        return context

class MyChampionshipView(LoginRequiredMixin, DetailView):
    model = Championship
    template_name = 'tournaments/my_championship.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'club'):
            messages.warning(request, "You need to create a club first.")
            return redirect('clubs:create_club')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        try:
            messages.info(self.request, "Начинаем поиск чемпионата...")
            
            # Проверяем наличие активного сезона
            active_season = Season.objects.filter(is_active=True).first()
            if not active_season:
                messages.error(self.request, "В системе нет активного сезона!")
                raise Http404("No active season found")
            
            messages.info(self.request, f"Найден активный сезон: {active_season}")
            
            # Проверяем клуб пользователя
            user_club = self.request.user.club
            messages.info(
                self.request, 
                f"Информация о клубе: ID={user_club.id}, "
                f"Name={user_club.name}, League={user_club.league}"
            )
            
            # Получаем информацию обо всех чемпионатах
            all_championships = Championship.objects.filter(season=active_season)
            messages.info(
                self.request, 
                f"Всего чемпионатов в сезоне: {all_championships.count()}"
            )
            
            # Ищем чемпионат с нашей командой
            championship = Championship.objects.select_related(
                'league',
                'season'
            ).get(
                teams=user_club,
                season__is_active=True
            )
            
            if championship:
                messages.info(
                    self.request,
                    f"Найден чемпионат: {championship.league.name}, "
                    f"всего команд: {championship.teams.count()}"
                )
                return championship
            else:
                messages.error(self.request, "Чемпионат не найден!")
                raise Http404("No championship found for your club")
                
        except Season.DoesNotExist:
            messages.error(self.request, "Активный сезон не найден!")
            raise Http404("No active season found")
        except Championship.DoesNotExist:
            messages.error(
                self.request,
                "Не найден чемпионат для вашей команды! "
                "Возможно, команда не была добавлена в чемпионат."
            )
            raise Http404("No championship found for your club")
        except Exception as e:
            messages.error(self.request, f"Неожиданная ошибка: {str(e)}")
            raise Http404(str(e))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        championship = self.object
        user_club = self.request.user.club

        # Debug information
        context['debug'] = {
            'user_club': {
                'id': user_club.id,
                'name': user_club.name,
                'league': str(user_club.league) if user_club.league else None
            },
            'championship': {
                'id': championship.id,
                'name': str(championship),
                'team_count': championship.teams.count(),
                'teams': list(championship.teams.values_list('name', flat=True))
            }
        }

        # Check all championship matches
        all_matches = championship.championshipmatch_set.select_related(
            'match', 'match__home_team', 'match__away_team'
        )
        context['debug']['all_matches'] = {
            'total_count': all_matches.count(),
            'sample': [
                {
                    'round': m.round,
                    'home': m.match.home_team.name,
                    'away': m.match.away_team.name,
                    'date': m.match.date,
                }
                for m in all_matches[:5]  # Show first 5 matches
            ]
        }

        # Try to find matches for user's club
        home_matches = all_matches.filter(match__home_team=user_club)
        away_matches = all_matches.filter(match__away_team=user_club)
        
        context['debug']['club_matches'] = {
            'home_matches': {
                'count': home_matches.count(),
                'sample': [
                    {
                        'round': m.round,
                        'opponent': m.match.away_team.name,
                        'date': m.match.date
                    }
                    for m in home_matches[:3]
                ]
            },
            'away_matches': {
                'count': away_matches.count(),
                'sample': [
                    {
                        'round': m.round,
                        'opponent': m.match.home_team.name,
                        'date': m.match.date
                    }
                    for m in away_matches[:3]
                ]
            }
        }

        # Get standings
        context['standings'] = championship.championshipteam_set.select_related(
            'team'
        ).order_by(
            '-points', 
            '-goals_for'
        )

        # Get team matches for display
        team_matches = all_matches.filter(
            models.Q(match__home_team=user_club) | 
            models.Q(match__away_team=user_club)
        ).order_by('match__date')

        context['team_matches'] = team_matches
        
        # Count matches by status
        match_status = {}
        for m in team_matches:
            status = m.match.status
            match_status[status] = match_status.get(status, 0) + 1
        context['debug']['match_status'] = match_status

        return context

class ChampionshipCalendarView(LoginRequiredMixin, DetailView):
    model = Championship
    template_name = 'tournaments/championship_calendar.html'
    context_object_name = 'championship'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class SeasonListView(LoginRequiredMixin, ListView):
    model = Season
    template_name = 'tournaments/season_list.html'
    context_object_name = 'seasons'

class LeagueListView(LoginRequiredMixin, ListView):
    model = League
    template_name = 'tournaments/league_list.html'
    context_object_name = 'leagues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Базовая статистика
        context['standings'] = self.object.championshipteam_set.select_related(
            'team'
        ).order_by(
            '-points', 
            '-goals_for'
        )

        # Расширенная отладка для клуба
        user_club = self.request.user.club
        context['debug'] = {
            'club': {
                'name': user_club.name if user_club else 'No club',
                'id': user_club.id if user_club else 'No ID',
                'country': str(user_club.country) if user_club else 'No country',
                'league': user_club.league.name if user_club and user_club.league else 'No league'
            },
            'championship': {
                'id': self.object.id,
                'name': str(self.object),
                'total_matches': self.object.championshipmatch_set.count(),
                'total_teams': self.object.teams.count(),
                'teams': list(self.object.teams.values_list('name', 'id'))
            }
        }

        # Получаем примеры матчей
        sample_matches = self.object.championshipmatch_set.all()[:5].select_related(
            'match', 'match__home_team', 'match__away_team'
        )
        
        context['debug']['matches'] = [{
            'round': match.round,
            'home_team': {
                'name': match.match.home_team.name,
                'id': match.match.home_team.id
            },
            'away_team': {
                'name': match.match.away_team.name,
                'id': match.match.away_team.id
            }
        } for match in sample_matches]

        # Проверяем, есть ли клуб в чемпионате
        if user_club:
            team_in_championship = self.object.teams.filter(id=user_club.id).exists()
            context['debug']['club']['in_championship'] = team_in_championship
            
            # Попробуем найти матчи клуба
            team_matches = self.object.championshipmatch_set.filter(
                models.Q(match__home_team=user_club) | 
                models.Q(match__away_team=user_club)
            ).select_related(
                'match',
                'match__home_team',
                'match__away_team'
            )
            
            context['team_matches'] = team_matches.order_by('match__date')
            context['debug']['club']['matches_count'] = team_matches.count()

        return context
def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect(request.POST.get('next', '/'))
    else:
        return redirect('/')

def get_championship_matches(request, pk):
    championship = Championship.objects.get(pk=pk)
    matches = championship.championshipmatch_set.all().select_related(
        'match', 
        'match__home_team', 
        'match__away_team'
    )
    
    match_data = [{
        'id': match.id,
        'round': match.round,
        'date': match.match.date.isoformat(),
        'home_team': match.match.home_team.name,
        'away_team': match.match.away_team.name,
        'status': match.match.status,
        'score': f"{match.match.home_score}-{match.match.away_score}" if match.match.status == 'finished' else None
    } for match in matches]
    
    return JsonResponse({'matches': match_data})