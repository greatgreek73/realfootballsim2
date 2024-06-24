from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView
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
        return redirect(reverse('matches:team_selection', kwargs={'match_id': match.pk}))

class MatchDetailView(DetailView):
    model = Match
    template_name = 'matches/match_detail.html'

@login_required
def simulate_match_view(request, match_id):
    simulate_match(match_id)
    return redirect(reverse('matches:match_detail', kwargs={'pk': match_id}))

@login_required
def team_selection_view(request, match_id):
    match = Match.objects.get(pk=match_id)
    return render(request, 'matches/team_selection.html', {'match': match})

@login_required
@require_http_methods(["GET"])
def get_players(request, match_id):
    match = Match.objects.get(pk=match_id)
    if request.user.club == match.home_team:
        players = Player.objects.filter(club=match.home_team)
    elif request.user.club == match.away_team:
        players = Player.objects.filter(club=match.away_team)
    else:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    return JsonResponse([{
        'id': player.id,
        'name': f"{player.first_name} {player.last_name}",
        'position': player.position
    } for player in players], safe=False)

@login_required
@require_http_methods(["POST"])
def save_team_selection(request, match_id):
    match = Match.objects.get(pk=match_id)
    if request.user.club not in [match.home_team, match.away_team]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    selection = json.loads(request.body)
    
    # Здесь можно добавить дополнительную валидацию выбора

    TeamSelection.objects.update_or_create(
        match=match,
        club=request.user.club,
        defaults={'selection': selection}
    )
    
    return JsonResponse({'success': True})

@method_decorator(login_required, name='dispatch')
class MatchListView(ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'

    def get_queryset(self):
        return Match.objects.filter(home_team=self.request.user.club) | \
               Match.objects.filter(away_team=self.request.user.club)