from django.core.management.base import BaseCommand
from django.db import transaction
from clubs.models import Club
from tournaments.models import League
from django.db.models import Count

class Command(BaseCommand):
    help = 'Assigns clubs to leagues ensuring 16 teams per league'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Сначала очистим существующие привязки к лигам только для ботов
                Club.objects.filter(is_bot=True).update(league=None)

                # Получаем все лиги, сортируем по стране и уровню
                leagues = League.objects.all().order_by('country', 'level')
                
                # Для каждой страны отдельно обрабатываем клубы
                for league in leagues:
                    existing_clubs = Club.objects.filter(league=league).count()
                    if existing_clubs > 0:
                        self.stdout.write(f"League {league} already has {existing_clubs} clubs")
                        continue

                    # Берем только бот-клубы без лиги из той же страны
                    available_clubs = Club.objects.filter(
                        country=league.country,
                        league__isnull=True,
                        is_bot=True  # Только боты
                    )[:16]  # Берем только 16 клубов
                    
                    if available_clubs.count() < 16:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Not enough bot clubs for {league}. Found only {available_clubs.count()}"
                            )
                        )
                        continue

                    # Назначаем лигу для клубов
                    for club in available_clubs:
                        club.league = league
                        club.save()
                        
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Assigned {available_clubs.count()} bot clubs to {league}"
                        )
                    )

                # Проверяем результаты
                for league in leagues:
                    bot_count = Club.objects.filter(league=league, is_bot=True).count()
                    human_count = Club.objects.filter(league=league, is_bot=False).count()
                    self.stdout.write(f"{league}: {bot_count} bot teams, {human_count} human teams")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error occurred: {str(e)}"))
            raise e