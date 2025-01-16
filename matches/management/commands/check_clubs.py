from django.core.management.base import BaseCommand
from clubs.models import Club
from players.models import Player

class Command(BaseCommand):
    help = 'Checks clubs and their players'

    def handle(self, *args, **kwargs):
        clubs = Club.objects.all()
        
        self.stdout.write("\nClub statistics:")
        for club in clubs:
            player_count = Player.objects.filter(club=club).count()
            self.stdout.write(f"\nClub: {club.name}")
            self.stdout.write(f"Total players: {player_count}")
            
            # Проверяем количество игроков по позициям
            positions = Player.objects.filter(club=club).values_list('position', flat=True)
            position_counts = {}
            for pos in positions:
                position_counts[pos] = position_counts.get(pos, 0) + 1
                
            self.stdout.write("Players by position:")
            for pos, count in position_counts.items():
                self.stdout.write(f"  {pos}: {count}")
