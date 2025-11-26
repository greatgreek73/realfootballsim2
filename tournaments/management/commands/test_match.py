from django.core.management.base import BaseCommand
from django.utils import timezone
from clubs.models import Club
from matches.models import Match
from matches.match_simulation import MatchSimulation
import random

class Command(BaseCommand):
    help = 'Tests match simulation with random teams'

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

            # Инициализируем симуляцию
            simulation = MatchSimulation(match)
            
            # Симулируем матч
            self.stdout.write('\n=== НАЧАЛО МАТЧА ===\n')
            
            for minute in range(90):
                if minute % 15 == 0:  # Каждые 15 минут показываем статус
                    self.stdout.write(f'\n=== {minute} МИНУТА ===')
                    self.stdout.write(f'Счет: {match.home_score} - {match.away_score}')
                    self.stdout.write(f'Владение мячом: {simulation.match_stats["home"]["possession"]}% - {simulation.match_stats["away"]["possession"]}%')
                    self.stdout.write(f'Удары (в створ): {simulation.match_stats["home"]["shots"]} ({simulation.match_stats["home"]["shots_on_target"]}) - {simulation.match_stats["away"]["shots"]} ({simulation.match_stats["away"]["shots_on_target"]})')
                
                simulation.simulate_minute(minute)
            
            # Вывод итоговой статистики
            self.stdout.write('\n=== ИТОГОВАЯ СТАТИСТИКА ===')
            self.stdout.write(f'\nИтоговый счет: {match.home_score} - {match.away_score}')
            self.stdout.write('\nСтатистика домашней команды:')
            self.stdout.write(f'Владение мячом: {simulation.match_stats["home"]["possession"]}%')
            self.stdout.write(f'Удары (в створ): {simulation.match_stats["home"]["shots"]} ({simulation.match_stats["home"]["shots_on_target"]})')
            self.stdout.write(f'Угловые: {simulation.match_stats["home"]["corners"]}')
            self.stdout.write(f'Фолы: {simulation.match_stats["home"]["fouls"]}')
            self.stdout.write(f'Атаки (опасные): {simulation.match_stats["home"]["attacks"]} ({simulation.match_stats["home"]["dangerous_attacks"]})')
            
            self.stdout.write('\nСтатистика гостевой команды:')
            self.stdout.write(f'Владение мячом: {simulation.match_stats["away"]["possession"]}%')
            self.stdout.write(f'Удары (в створ): {simulation.match_stats["away"]["shots"]} ({simulation.match_stats["away"]["shots_on_target"]})')
            self.stdout.write(f'Угловые: {simulation.match_stats["away"]["corners"]}')
            self.stdout.write(f'Фолы: {simulation.match_stats["away"]["fouls"]}')
            self.stdout.write(f'Атаки (опасные): {simulation.match_stats["away"]["attacks"]} ({simulation.match_stats["away"]["dangerous_attacks"]})')
            
            # События матча
            self.stdout.write('\n=== СОБЫТИЯ МАТЧА ===')
            events = match.events.all().order_by('minute')
            for event in events:
                self.stdout.write(f'{event.minute}\' - {event.description}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nПроизошла ошибка: {str(e)}'))