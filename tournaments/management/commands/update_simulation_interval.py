from django.core.management.base import BaseCommand
from tournaments.celery_utils import ensure_simulation_schedule

class Command(BaseCommand):
    help = 'Update Celery beat interval for match simulation using MATCH_MINUTE_REAL_SECONDS.'

    def handle(self, *args, **options):
        ensure_simulation_schedule()
        self.stdout.write(self.style.SUCCESS('Simulation interval updated'))
