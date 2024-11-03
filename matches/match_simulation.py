import random
from .models import Match, MatchEvent
from players.models import Player

def simulate_match(match_id):
    match = Match.objects.get(id=match_id)
    match.status = 'in_progress'
    match.save()

    # Базовая логика симуляции
    for minute in range(1, 91):
        if random.random() < 0.05:  # 5% шанс гола каждую минуту
            scoring_team = random.choice([match.home_team, match.away_team])
            if scoring_team == match.home_team:
                match.home_score += 1
                scorer = random.choice(Player.objects.filter(club=match.home_team))
            else:
                match.away_score += 1
                scorer = random.choice(Player.objects.filter(club=match.away_team))
            
            MatchEvent.objects.create(
                match=match,
                minute=minute,
                event_type='goal',
                player=scorer,
                description=f"Goal scored by {scorer.first_name} {scorer.last_name}"
            )

    match.status = 'finished'
    match.save()