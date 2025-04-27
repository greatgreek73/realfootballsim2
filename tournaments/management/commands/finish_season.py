from django.core.management.base import BaseCommand
from django.db import transaction
from matches.models import Match

class Command(BaseCommand):
    help = "Завершить сразу все матчи сезона (тест-режим)."

    def handle(self, *args, **options):
        with transaction.atomic():
            qs = Match.objects.exclude(status='finished')
            total = qs.count()
            for m in qs:
                m.home_score = m.home_score or 0
                m.away_score = m.away_score or 0
                m.current_minute = 90
                m.status = 'finished'
                m.save(update_fields=[
                    'home_score', 'away_score', 'current_minute', 'status'
                ])
        self.stdout.write(self.style.SUCCESS(
            f'Завершено матчей: {total}'
        ))
