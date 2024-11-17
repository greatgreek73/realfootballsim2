from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from tournaments.models import Championship, ChampionshipMatch
from matches.models import Match
from clubs.models import Club
import logging

logger = logging.getLogger(__name__)

def update_matches_for_replaced_team(championship, old_team_id, new_team):
    """
    Обновляет все матчи, заменяя old_team на new_team
    """
    try:
        with transaction.atomic():
            # Найти все матчи, где участвовала старая команда
            matches = Match.objects.filter(
                championshipmatch__championship=championship
            ).filter(
                Q(home_team_id=old_team_id) |
                Q(away_team_id=old_team_id)
            )
            
            updated_count = 0
            # Обновить все найденные матчи
            for match in matches:
                if match.home_team_id == old_team_id:
                    match.home_team = new_team
                    updated_count += 1
                if match.away_team_id == old_team_id:
                    match.away_team = new_team
                    updated_count += 1
                match.save()
                logger.info(f"Updated match {match.id}: {match.home_team} vs {match.away_team}")
            
            return updated_count  # Возвращаем количество обновленных матчей
    except Exception as e:
        logger.error(f"Error updating matches: {str(e)}")
        raise

class Command(BaseCommand):
    help = 'Updates championship matches for a club, replacing a bot team'

    def add_arguments(self, parser):
        parser.add_argument('club_id', type=int, help='ID of the club to update matches for')

    def handle(self, *args, **options):
        club_id = options['club_id']
        
        try:
            with transaction.atomic():
                # Получаем клуб
                club = Club.objects.get(id=club_id)
                self.stdout.write(f"Found club: {club.name} (ID: {club.id})")
                
                # Находим активный чемпионат для страны клуба
                championship = Championship.objects.get(
                    league__country=club.country,
                    league__level=1,
                    season__is_active=True
                )
                self.stdout.write(f"Found championship: {championship}")

                # Проверяем, есть ли клуб в чемпионате
                is_in_championship = championship.teams.filter(id=club.id).exists()
                if not is_in_championship:
                    self.stdout.write(self.style.ERROR(f"Club {club.name} is not part of championship {championship}"))
                    return

                # Получаем все матчи чемпионата
                matches = Match.objects.filter(
                    championshipmatch__championship=championship
                )

                # Находим матчи, где клуб должен участвовать
                team_matches = matches.filter(
                    Q(home_team=club) |
                    Q(away_team=club)
                ).count()

                if team_matches == 0:
                    # Клуб в чемпионате, но нет матчей - ищем бота, которого он заменил
                    self.stdout.write("Looking for replaced bot team...")
                    
                    # Выводим все команды в чемпионате для отладки
                    self.stdout.write("\nTeams in championship:")
                    for team in championship.teams.all():
                        self.stdout.write(f"- {team.name} (ID: {team.id}, Bot: {team.is_bot})")
                    
                    # Проверяем статистику
                    from tournaments.models import ChampionshipTeam
                    team_stats = ChampionshipTeam.objects.filter(
                        championship=championship,
                        team=club
                    ).first()
                    
                    if team_stats:
                        self.stdout.write(f"\nFound team statistics:")
                        self.stdout.write(f"Points: {team_stats.points}")
                        self.stdout.write(f"Matches played: {team_stats.matches_played}")
                    else:
                        self.stdout.write(self.style.WARNING("No team statistics found!"))

                    # Выводим пример нескольких матчей для отладки
                    self.stdout.write("\nSample matches in championship:")
                    for match in matches[:5]:
                        self.stdout.write(
                            f"- {match.home_team.name} vs {match.away_team.name}"
                        )

                    # Находим команды-боты с таким же количеством очков
                    if team_stats:
                        potential_bots = ChampionshipTeam.objects.filter(
                            championship=championship,
                            points=team_stats.points,
                            team__is_bot=True
                        )
                        
                        self.stdout.write(f"\nFound {potential_bots.count()} potential bot matches:")
                        for bot_stats in potential_bots:
                            self.stdout.write(
                                f"- {bot_stats.team.name} "
                                f"(Points: {bot_stats.points}, "
                                f"Matches: {bot_stats.matches_played})"
                            )
                    
                    # Спрашиваем пользователя об ID бота
                    bot_id = input("\nEnter the ID of the bot team to replace: ")
                    try:
                        bot_id = int(bot_id)
                        replaced_matches = update_matches_for_replaced_team(
                            championship=championship,
                            old_team_id=bot_id,
                            new_team=club
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully updated {replaced_matches} matches "
                                f"for club {club.name}"
                            )
                        )
                    except ValueError:
                        self.stdout.write(self.style.ERROR("Invalid bot ID!"))
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Club {club.name} already has {team_matches} matches "
                            f"in championship {championship}"
                        )
                    )

        except Club.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Club with ID {club_id} not found"))
        except Championship.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"No active championship found for club {club.name} "
                    f"in country {club.country}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))