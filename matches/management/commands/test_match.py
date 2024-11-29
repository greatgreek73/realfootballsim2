from django.core.management.base import BaseCommand
from django.utils import timezone
from clubs.models import Club
from matches.models import Match
from matches.match_simulation import MatchSimulation
import random

class Command(BaseCommand):
    help = 'Tests match simulation with random teams'

    def handle(self, *args, **options):
        try:
            # Get random teams
            teams = list(Club.objects.all().order_by('?')[:2])
            if len(teams) < 2:
                self.stdout.write(self.style.ERROR('Not enough teams in database'))
                return

            home_team = teams[0]
            away_team = teams[1]

            # Display team information
            self.stdout.write('\nTeam Information:')
            self.stdout.write(f'\nHome team: {home_team.name}')
            self.stdout.write(f'Players: {home_team.player_set.count()}')
            
            self.stdout.write(f'\nAway team: {away_team.name}')
            self.stdout.write(f'Players: {away_team.player_set.count()}\n')

            # Create test match
            match = Match.objects.create(
                home_team=home_team,
                away_team=away_team,
                date=timezone.now(),
                status='scheduled'
            )

            # Initialize simulation
            simulation = MatchSimulation(match)
            
            # Simulate match
            self.stdout.write('\n=== MATCH START ===\n')
            
            for minute in range(90):
                if minute % 5 == 0:  # Show status every 5 minutes
                    self.stdout.write(f'\n=== MINUTE {minute} ===')
                    self.stdout.write(f'Score: {match.home_score} - {match.away_score}')
                    self.stdout.write(f'Possession: {simulation.match_stats["home"]["possession"]}% - {simulation.match_stats["away"]["possession"]}%')
                    self.stdout.write(f'Shots (on target): {simulation.match_stats["home"]["shots"]} ({simulation.match_stats["home"]["shots_on_target"]}) - {simulation.match_stats["away"]["shots"]} ({simulation.match_stats["away"]["shots_on_target"]})')
                
                simulation.simulate_minute(minute)
                
                # Show events immediately after they happen
                events = match.events.filter(minute=minute)
                for event in events:
                    self.stdout.write(f'{event.minute}\' - {event.description}')
            
            # Final statistics
            self.stdout.write('\n=== FINAL STATISTICS ===')
            self.stdout.write(f'\nFinal score: {match.home_score} - {match.away_score}')
            
            self.stdout.write('\nHome team statistics:')
            self.stdout.write(f'Possession: {simulation.match_stats["home"]["possession"]}%')
            self.stdout.write(f'Shots (on target): {simulation.match_stats["home"]["shots"]} ({simulation.match_stats["home"]["shots_on_target"]})')
            self.stdout.write(f'Corners: {simulation.match_stats["home"]["corners"]}')
            self.stdout.write(f'Fouls: {simulation.match_stats["home"]["fouls"]}')
            self.stdout.write(f'Attacks (dangerous): {simulation.match_stats["home"]["attacks"]} ({simulation.match_stats["home"]["dangerous_attacks"]})')
            
            self.stdout.write('\nAway team statistics:')
            self.stdout.write(f'Possession: {simulation.match_stats["away"]["possession"]}%')
            self.stdout.write(f'Shots (on target): {simulation.match_stats["away"]["shots"]} ({simulation.match_stats["away"]["shots_on_target"]})')
            self.stdout.write(f'Corners: {simulation.match_stats["away"]["corners"]}')
            self.stdout.write(f'Fouls: {simulation.match_stats["away"]["fouls"]}')
            self.stdout.write(f'Attacks (dangerous): {simulation.match_stats["away"]["attacks"]} ({simulation.match_stats["away"]["dangerous_attacks"]})')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nError occurred: {str(e)}'))