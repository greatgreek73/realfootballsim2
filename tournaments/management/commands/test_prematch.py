from django.core.management.base import BaseCommand
from django.utils import timezone
from clubs.models import Club
from matches.models import Match
from matches.match_preparation import PreMatchPreparation
import random

class Command(BaseCommand):
    help = 'Tests prematch preparation with random teams'

    def handle(self, *args, **options):
        try:
            # Получаем две случайные команды
            teams = list(Club.objects.all().order_by('?')[:2])
            if len(teams) < 2:
                self.stdout.write(self.style.ERROR('Недостаточно команд в базе данных'))
                return

            home_team = teams[0]
            away_team = teams[1]

            # Выводим информацию о командах до создания матча
            self.stdout.write('\nИнформация о командах:')
            self.stdout.write(f'\nДомашняя команда: {home_team.name}')
            self.stdout.write(f'Количество игроков: {home_team.player_set.count()}')
            
            self.stdout.write(f'\nГостевая команда: {away_team.name}')
            self.stdout.write(f'Количество игроков: {away_team.player_set.count()}\n')

            # Создаем тестовый матч
            match = Match.objects.create(
                home_team=home_team,
                away_team=away_team,
                date=timezone.now(),
                status='scheduled'
            )

            # Инициализируем подготовку матча
            prep = PreMatchPreparation(match)
            
            # Проводим подготовку
            if prep.prepare_match():
                self.stdout.write(self.style.SUCCESS('\nПредматчевая подготовка успешна!\n'))
                
                # Выводим информацию о командах
                self.stdout.write('\n=== ИНФОРМАЦИЯ О КОМАНДАХ ===')
                self.stdout.write(f'\nДомашняя команда: {home_team.name}')
                self.stdout.write(f'Гостевая команда: {away_team.name}\n')
                
                # Выводим общую силу команд
                self.stdout.write('\n=== ОБЩАЯ СИЛА КОМАНД ===')
                self.stdout.write(f'Домашняя команда: {prep.team_strengths["home"]}')
                self.stdout.write(f'Гостевая команда: {prep.team_strengths["away"]}\n')
                
                # Выводим детальные параметры
                self.stdout.write('\n=== ПАРАМЕТРЫ ДОМАШНЕЙ КОМАНДЫ ===')
                home_params = prep.match_parameters['home']
                self.stdout.write(f'Атака: {home_params["team_attack"]}')
                self.stdout.write(f'Оборона: {home_params["team_defense"]}')
                self.stdout.write(f'Полузащита: {home_params["team_midfield"]}')
                self.stdout.write(f'Сила вратаря: {home_params["goalkeeper_strength"]}\n')
                
                self.stdout.write('\n=== ПАРАМЕТРЫ ГОСТЕВОЙ КОМАНДЫ ===')
                away_params = prep.match_parameters['away']
                self.stdout.write(f'Атака: {away_params["team_attack"]}')
                self.stdout.write(f'Оборона: {away_params["team_defense"]}')
                self.stdout.write(f'Полузащита: {away_params["team_midfield"]}')
                self.stdout.write(f'Сила вратаря: {away_params["goalkeeper_strength"]}\n')
                
            else:
                self.stdout.write(self.style.ERROR('\nОшибки при подготовке матча:'))
                for error in prep.get_validation_errors():
                    self.stdout.write(self.style.ERROR(f'- {error}'))
            
            # Удаляем тестовый матч
            match.delete()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nПроизошла ошибка: {str(e)}'))