from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from tournaments.models import Season, Championship
from django.core.management import call_command
from django.db.models import Count, Q

class Command(BaseCommand):
    help = 'Handles the end of season process'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force end season even if not all matches are finished'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Получаем текущий активный сезон
                current_season = Season.objects.get(is_active=True)
                
                # Проверяем завершение всех матчей
                championships = Championship.objects.filter(season=current_season)
                
                unfinished_matches = 0
                for championship in championships:
                    unfinished = championship.championshipmatch_set.filter(
                        ~Q(match__status='finished')
                    ).count()
                    unfinished_matches += unfinished
                
                if unfinished_matches > 0 and not options['force']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Cannot end season: {unfinished_matches} matches not finished. "
                            "Use --force to override."
                        )
                    )
                    return
                
                # Проверяем все чемпионаты на правильное количество команд
                invalid_championships = []
                for championship in championships:
                    team_count = championship.teams.count()
                    if team_count != 16:
                        invalid_championships.append(
                            f"{championship}: {team_count} teams"
                        )
                
                if invalid_championships and not options['force']:
                    self.stdout.write(
                        self.style.WARNING(
                            "Invalid team counts in championships:\n" + 
                            "\n".join(invalid_championships) +
                            "\nUse --force to override."
                        )
                    )
                    return

                # Завершаем текущий сезон
                self.stdout.write("Processing end of season transitions...")
                
                # Обрабатываем переходы между дивизионами
                call_command('handle_season_transitions')
                
                # Деактивируем текущий сезон
                current_season.is_active = False
                current_season.save()
                
                # Создаем новый сезон
                self.stdout.write("Creating new season...")
                call_command('create_new_season')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully ended season {current_season.number}"
                    )
                )

        except Season.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("No active season found")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error ending season: {str(e)}")
            )
            raise

    def validate_championship_results(self, championship):
        """
        Проверяет корректность результатов чемпионата
        """
        # Проверяем количество сыгранных матчей для каждой команды
        team_stats = championship.championshipteam_set.all()
        total_teams = team_stats.count()
        expected_matches = (total_teams - 1) * 2  # Каждая команда играет со всеми дважды
        
        for stats in team_stats:
            if stats.matches_played != expected_matches:
                return False, f"Team {stats.team.name} played {stats.matches_played} matches instead of {expected_matches}"
        
        return True, None