from .models import Match, MatchEvent, TeamSelection
from players.models import Player
import random

def simulate_match(match_id):
    match = Match.objects.get(id=match_id)
    home_selection = TeamSelection.objects.get(club=match.home_team)
    away_selection = TeamSelection.objects.get(club=match.away_team)

    home_players = [Player.objects.get(id=player_id) for player_id in home_selection.selection.values()]
    away_players = [Player.objects.get(id=player_id) for player_id in away_selection.selection.values()]

    match.status = 'in_progress'
    match.save()

    for minute in range(1, 91):
        if random.random() < 0.05:  # 5% шанс гола каждую минуту
            scoring_team = random.choice([match.home_team, match.away_team])
            if scoring_team == match.home_team:
                match.home_score += 1
                scorer = random.choice(home_players)
            else:
                match.away_score += 1
                scorer = random.choice(away_players)
            
            MatchEvent.objects.create(
                match=match,
                minute=minute,
                event_type='goal',
                player=scorer,
                description=f"Goal scored by {scorer.first_name} {scorer.last_name}"
            )

        # Можно добавить другие события, такие как желтые карточки, красные карточки, травмы и т.д.
        if random.random() < 0.02:  # 2% шанс желтой карточки
            team = random.choice([match.home_team, match.away_team])
            player = random.choice(home_players if team == match.home_team else away_players)
            MatchEvent.objects.create(
                match=match,
                minute=minute,
                event_type='yellow_card',
                player=player,
                description=f"Yellow card for {player.first_name} {player.last_name}"
            )

    match.status = 'finished'
    match.save()