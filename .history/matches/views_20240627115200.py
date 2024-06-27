from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Match
from .match_simulation import simulate_match

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

@method_decorator(login_required, name='dispatch')
class MatchListView(ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'

    def get_queryset(self):
        return Match.objects.filter(home_team=self.request.user.club) | \
               Match.objects.filter(away_team=self.request.user.club)