from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import Match, MatchEvent
from clubs.models import Club
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['match_events'] = MatchEvent.objects.filter(match=self.object).order_by('minute')
        return context

@login_required
def simulate_match_view(request, match_id):
    # Если match_id = 0, создаем новый тестовый матч
    if match_id == 0:
        # Получаем клуб пользователя
        club = request.user.club
        # Выбираем случайного бота-соперника
        opponent = Club.objects.filter(is_bot=True).exclude(id=club.id).order_by('?').first()
        if not opponent:
            return render(request, 'matches/no_opponent.html', {'club': club})
        
        # Создаем новый матч
        match = Match.objects.create(
            home_team=club,
            away_team=opponent,
            date=timezone.now(),
            status='scheduled'
        )
        match_id = match.id
    
    # Запускаем симуляцию матча
    simulate_match(match_id)
    
    # Получаем обновленный матч и события
    match = get_object_or_404(Match, id=match_id)
    match_events = MatchEvent.objects.filter(match=match).order_by('minute')
    
    # Отображаем страницу с результатами матча
    return render(request, 'matches/match_detail.html', {
        'match': match,
        'match_events': match_events,
    })

@method_decorator(login_required, name='dispatch')
class MatchListView(ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'

    def get_queryset(self):
        return Match.objects.filter(home_team=self.request.user.club) | \
               Match.objects.filter(away_team=self.request.user.club)