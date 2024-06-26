from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Match, TeamSelection
from .match_simulation import simulate_match
from players.models import Player
import json

class CreateMatchView(CreateView):
    model = Match
    fields = ['home_team', 'away_team', 'date']
    template_name = 'matches/create_match.html'

    def form_valid(self, form):
        match = form.save()
        return redirect(reverse('matches:match_detail', kwargs={'pk': match.pk}))

class MatchDetailView(DetailView):
    model = Match
    template_name = 'matches/match_detail.html'

@login_required
def simulate_match_view(request, match_id):
    simulate_match(match_id)
    return redirect(reverse('matches:match_detail', kwargs={'pk': match_id}))

@login_required
def team_selection_view(request):
    club = request.user.club
    team_selection, created = TeamSelection.objects.get_or_create(club=club)
    
    if request.method == 'POST':
        selection = json.loads(request.body)
        team_selection.update_selection(selection)
        team_selection.complete_selection()
        return JsonResponse({'success': True})

    selection = team_selection.get_or_create_selection()
    players = Player.objects.filter(club=club)
    
    context = {
        'club': club,
        'players': players,
        'selection': selection,
    }
    return render(request, 'matches/team_selection.html', context)

@method_decorator(login_required, name='dispatch')
class MatchListView(ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'

    def get_queryset(self):
        return Match.objects.filter(home_team=self.request.user.club) | \
               Match.objects.filter(away_team=self.request.user.club)

@login_required
def view_team_selection(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    team_selection = get_object_or_404(TeamSelection, club=request.user.club)
    
    selected_players = []
    for position, player_id in team_selection.selection.items():
        player = get_object_or_404(Player, id=player_id)
        selected_players.append({
            'position': position,
            'name': f"{player.first_name} {player.last_name}",
            'actual_position': player.position
        })
    
    context = {
        'match': match,
        'selected_players': selected_players
    }
    return render(request, 'matches/view_team_selection.html', context)