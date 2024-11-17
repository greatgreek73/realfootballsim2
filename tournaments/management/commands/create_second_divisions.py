# tournaments/management/commands/create_second_divisions.py
from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import League
from django_countries import countries

class Command(BaseCommand):
    help = 'Creates second divisions for all countries'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                top_leagues = League.objects.filter(level=1)
                
                for league in top_leagues:
                    # Проверяем, нет ли уже второго дивизиона
                    second_div_exists = League.objects.filter(
                        country=league.country,
                        level=2
                    ).exists()
                    
                    if not second_div_exists:
                        League.objects.create(
                            name=f"{league.country.name} Second Division",
                            country=league.country,
                            level=2,
                            max_teams=16,
                            foreign_players_limit=5
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created second division for {league.country.name}"
                            )
                        )
                
                self.stdout.write(self.style.SUCCESS("All second divisions created!"))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error creating second divisions: {str(e)}")
            )