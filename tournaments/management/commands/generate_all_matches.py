from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import Championship
from tournaments.utils import create_championship_matches
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generates matches for all divisions'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Получаем все активные чемпионаты
                championships = Championship.objects.filter(
                    status='in_progress'
                ).select_related('league')
                
                total_matches = 0
                for championship in championships:
                    self.stdout.write(
                        f"Generating matches for {championship} "
                        f"(Division {championship.league.level})"
                    )
                    create_championship_matches(championship)
                    matches_count = championship.championshipmatch_set.count()
                    total_matches += matches_count
                    self.stdout.write(
                        f"Created {matches_count} matches for "
                        f"{championship.league.name} (Division {championship.league.level})"
                    )
                    
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully generated {total_matches} matches '
                        f'for {championships.count()} championships'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating matches: {str(e)}')
            )
            logger.error(f"Error generating matches: {str(e)}")