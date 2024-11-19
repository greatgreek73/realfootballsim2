from django.core.management.base import BaseCommand
from django.db import transaction
from tournaments.models import Championship, Season, League
from django.db.models import F
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Process end of season transitions between divisions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--season',
            type=int,
            help='Season number to process (defaults to active season)'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Получаем сезон для обработки
                season_number = options.get('season')
                if season_number:
                    season = Season.objects.get(number=season_number)
                else:
                    season = Season.objects.get(is_active=True)

                self.stdout.write(f"Processing end of season transitions for {season}")

                # Получаем все чемпионаты текущего сезона
                championships = Championship.objects.filter(
                    season=season
                ).select_related('league')

                # Группируем чемпионаты по странам
                countries = {}
                for champ in championships:
                    country_code = champ.league.country.code
                    if country_code not in countries:
                        countries[country_code] = {'div1': None, 'div2': None}
                    
                    if champ.league.level == 1:
                        countries[country_code]['div1'] = champ
                    elif champ.league.level == 2:
                        countries[country_code]['div2'] = champ

                # Обрабатываем каждую страну
                for country_code, divisions in countries.items():
                    if not divisions['div1'] or not divisions['div2']:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping {country_code} - missing division"
                            )
                        )
                        continue

                    self.process_country_transitions(
                        divisions['div1'], 
                        divisions['div2']
                    )

        except Season.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("No active season found!")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error during transitions: {str(e)}")
            )
            raise

    def process_country_transitions(self, div1_championship, div2_championship):
        """
        Обработка переходов между дивизионами для одной страны
        """
        country_name = div1_championship.league.country.name
        self.stdout.write(f"\nProcessing {country_name}:")

        try:
            # Получаем команды для понижения (2 последние из первого дивизиона)
            relegated_teams = (
                div1_championship.championshipteam_set
                .annotate(
                    goals_diff=F('goals_for') - F('goals_against')
                )
                .order_by(
                    'points',
                    'goals_diff',
                    'goals_for'
                )[:2]
            )

            # Получаем команды для повышения (2 первые из второго дивизиона)
            promoted_teams = (
                div2_championship.championshipteam_set
                .annotate(
                    goals_diff=F('goals_for') - F('goals_against')
                )
                .order_by(
                    '-points',
                    '-goals_diff',
                    '-goals_for'
                )[:2]
            )

            # Применяем переходы
            div2_league = div2_championship.league
            div1_league = div1_championship.league

            # Понижаем команды
            for team_stats in relegated_teams:
                team = team_stats.team
                team.league = div2_league
                team.save()
                self.stdout.write(
                    f"  Relegated: {team.name} "
                    f"(Points: {team_stats.points}, "
                    f"GD: {team_stats.goals_diff})"
                )

            # Повышаем команды
            for team_stats in promoted_teams:
                team = team_stats.team
                team.league = div1_league
                team.save()
                self.stdout.write(
                    f"  Promoted: {team.name} "
                    f"(Points: {team_stats.points}, "
                    f"GD: {team_stats.goals_diff})"
                )

        except Exception as e:
            raise ValidationError(
                f"Error processing transitions for {country_name}: {str(e)}"
            )