from django.core.management.base import BaseCommand
from django.db import transaction
from clubs.models import Club
from tournaments.models import League
from django.db.models import Count

class Command(BaseCommand):
    help = 'Checks current distribution of clubs in leagues'

    def handle(self, *args, **options):
        # Считаем команды без лиги
        unassigned_clubs = Club.objects.filter(league__isnull=True).count()
        self.stdout.write(f"\nКоманды без лиги: {unassigned_clubs}")

        # Группируем по странам
        countries = set(Club.objects.values_list('country', flat=True))
        
        self.stdout.write("\nРаспределение по странам:")
        for country in sorted(countries):
            clubs = Club.objects.filter(country=country)
            leagues = League.objects.filter(country=country).order_by('level')
            
            self.stdout.write(f"\n{country}:")
            self.stdout.write(f"Всего команд: {clubs.count()}")
            self.stdout.write(f"Количество лиг: {leagues.count()}")
            
            if leagues.exists():
                self.stdout.write("Распределение по лигам:")
                for league in leagues:
                    club_count = Club.objects.filter(league=league).count()
                    self.stdout.write(f"  {league.name} (уровень {league.level}): {club_count} команд")
            
            unassigned = clubs.filter(league__isnull=True).count()
            if unassigned > 0:
                self.stdout.write(f"Не распределено: {unassigned} команд")