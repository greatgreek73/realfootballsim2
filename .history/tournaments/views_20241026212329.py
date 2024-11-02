from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Championship, Season, League
from django.db.models import F  # Добавляем этот импорт

class ChampionshipListView(LoginRequiredMixin, ListView):
    """Display list of all championships"""
    model = Championship
    template_name = 'tournaments/championship_list.html'
    context_object_name = 'championships'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_seasons'] = Season.objects.filter(is_active=True)
        return context

class ChampionshipDetailView(LoginRequiredMixin, DetailView):
    """Display championship details including standings"""
    model = Championship
    template_name = 'tournaments/championship_detail.html'
    context_object_name = 'championship'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Используем простую сортировку без аннотаций
        context['standings'] = self.object.championshipteam_set.all().order_by(
            '-points',
            '-goals_for'  # используем goals_for вместо goals_difference для сортировки
        )
        context['matches'] = self.object.championshipmatch_set.all().select_related(
            'match', 
            'match__home_team', 
            'match__away_team'
        ).order_by('round', 'match_day')
        return context

class SeasonListView(LoginRequiredMixin, ListView):
    """Display list of all seasons"""
    model = Season
    template_name = 'tournaments/season_list.html'
    context_object_name = 'seasons'

class LeagueListView(LoginRequiredMixin, ListView):
    """Display list of all leagues"""
    model = League
    template_name = 'tournaments/league_list.html'
    context_object_name = 'leagues'