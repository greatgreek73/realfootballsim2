from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import Championship
from tournaments.utils import create_championship_matches, validate_championship_schedule
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generates match schedule for championships'

    def add_arguments(self, parser):
        parser.add_argument(
            '--championship',
            type=int,
            help='ID конкретного чемпионата (если не указан, генерируется для всех активных)'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                if options['championship']:
                    championships = Championship.objects.filter(
                        id=options['championship'],
                        status='pending'
                    )
                else:
                    championships = Championship.objects.filter(
                        season__is_active=True,
                        status='pending'
                    )

                if not championships:
                    self.stdout.write(
                        self.style.WARNING('Нет чемпионатов для генерации расписания')
                    )
                    return

                for championship in championships:
                    try:
                        self.stdout.write(
                            f'Генерация расписания для {championship}...'
                        )
                        
                        create_championship_matches(championship)
                        
                        if validate_championship_schedule(championship):
                            championship.status = 'in_progress'
                            championship.save()
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Успешно сгенерировано расписание для {championship}'
                                )
                            )
                        else:
                            raise ValueError(
                                f'Ошибка валидации расписания для {championship}'
                            )
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Ошибка для {championship}: {str(e)}')
                        )
                        raise

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка генерации расписания: {str(e)}')
            )