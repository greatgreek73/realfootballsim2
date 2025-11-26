from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from clubs.models import Club
from tournaments.models import Championship, ChampionshipTeam, ChampionshipMatch, Season
from matches.models import Match
from django.db import transaction
from django.db.models import Q
from django.core.management import call_command

def update_matches_for_replaced_team(championship, old_team_id, new_team):
    """
    Обновляет все матчи, заменяя old_team на new_team
    """
    try:
        with transaction.atomic():
            # Находим все матчи старой команды
            bot_matches = Match.objects.filter(
                championshipmatch__championship=championship
            ).filter(
                Q(home_team_id=old_team_id) | Q(away_team_id=old_team_id)
            ).select_related(
                'championshipmatch',
                'home_team',
                'away_team'
            ).order_by('championshipmatch__round')

            # Обновляем каждый матч
            updated_count = 0
            unique_opponents = set()

            for match in bot_matches:
                # Получаем противника
                opponent = match.away_team if match.home_team_id == old_team_id else match.home_team
                unique_opponents.add(opponent.id)
                
                # Обновляем команду в матче
                if match.home_team_id == old_team_id:
                    match.home_team = new_team
                else:
                    match.away_team = new_team

                match.save()
                updated_count += 1

            # Проверка на количество уникальных противников
            if len(unique_opponents) < 2:
                raise ValueError(
                    f"Error: team has only {len(unique_opponents)} opponents. "
                    f"Something is wrong with the schedule."
                )

            return updated_count

    except Exception as e:
        raise

@receiver(post_save, sender=Club)
def handle_club_creation(sender, instance, created, **kwargs):
    """Обрабатывает создание нового клуба и замещение бота"""
    if not created or instance.is_bot:
        return
        
    try:
        with transaction.atomic():
            # Найти активный чемпионат
            championship = Championship.objects.select_related('season')\
                .filter(
                    league__country=instance.country,
                    league__level=1,
                    season__is_active=True
                ).first()
                
            if not championship:
                return

            # Проверяем, не добавлен ли уже клуб
            if championship.teams.filter(id=instance.id).exists():
                return
                
            # Найти команду-бота для замены
            bot_team = championship.teams.filter(is_bot=True).first()
            if not bot_team:
                return
            
            # Сохраняем ID бота перед удалением
            bot_team_id = bot_team.id
                
            # Получаем статистику бота
            bot_stats = ChampionshipTeam.objects.get(
                championship=championship,
                team=bot_team
            )
            
            # Создаем запись для нового клуба
            ChampionshipTeam.objects.create(
                championship=championship,
                team=instance,
                points=bot_stats.points,
                matches_played=bot_stats.matches_played,
                wins=bot_stats.wins,
                draws=bot_stats.draws,
                losses=bot_stats.losses,
                goals_for=bot_stats.goals_for,
                goals_against=bot_stats.goals_against
            )
            
            # Обновляем матчи
            update_matches_for_replaced_team(
                championship=championship,
                old_team_id=bot_team_id,
                new_team=instance
            )
            
            # Удаляем бота
            bot_stats.delete()
            bot_team.delete()
            
    except Exception as e:
        raise

@receiver(post_save, sender=Match)
def handle_match_result(sender, instance, **kwargs):
    """Обновляет статистику команд после завершения матча"""
    try:
        championship_match = ChampionshipMatch.objects.select_related(
            'championship',
            'match',
            'match__home_team',
            'match__away_team'
        ).filter(match=instance).first()

        if not championship_match or championship_match.processed or instance.status != 'finished':
            return

        max_attempts = 3
        current_attempt = 0

        while current_attempt < max_attempts:
            try:
                with transaction.atomic():
                    # Получаем статистику команд
                    home_stats = ChampionshipTeam.objects.select_for_update().get(
                        championship=championship_match.championship,
                        team=instance.home_team
                    )
                    away_stats = ChampionshipTeam.objects.select_for_update().get(
                        championship=championship_match.championship,
                        team=instance.away_team
                    )

                    # Обновляем статистику
                    home_stats.matches_played += 1
                    away_stats.matches_played += 1
                    home_stats.goals_for += instance.home_score
                    home_stats.goals_against += instance.away_score
                    away_stats.goals_for += instance.away_score
                    away_stats.goals_against += instance.home_score

                    # Обновляем результаты
                    if instance.home_score > instance.away_score:
                        home_stats.wins += 1
                        home_stats.points += 3
                        away_stats.losses += 1
                    elif instance.home_score < instance.away_score:
                        away_stats.wins += 1
                        away_stats.points += 3
                        home_stats.losses += 1
                    else:
                        home_stats.draws += 1
                        away_stats.draws += 1
                        home_stats.points += 1
                        away_stats.points += 1

                    # Сохраняем изменения
                    home_stats.save()
                    away_stats.save()

                    # Проверяем завершение чемпионата
                    championship = championship_match.championship
                    if championship.is_completed and championship.status != 'finished':
                        championship.status = 'finished'
                        championship.save()

                    championship_match.processed = True
                    championship_match.save()
                    return

            except Exception:
                current_attempt += 1
                if current_attempt == max_attempts:
                    raise
                import time
                time.sleep(1)

    except Exception:
        raise

@receiver(post_save, sender=Season)
def handle_season_end(sender, instance, **kwargs):
    """Обрабатывает окончание сезона"""
    # Проверяем, что сезон был активным, но стал неактивным
    if not instance.is_active and kwargs.get('update_fields') and 'is_active' in kwargs['update_fields']:
        try:
            with transaction.atomic():
                # Запускаем процесс переходов между дивизионами
                call_command('handle_season_transitions')
        except Exception as e:
            raise

@receiver(post_save, sender=ChampionshipTeam)
def update_team_league(sender, instance, **kwargs):
    """Обновляет привязку команды к лиге при изменении статистики"""
    if instance.championship.status == 'finished':
        try:
            with transaction.atomic():
                team = instance.team
                
                # Получаем текущую позицию команды
                position = instance.position
                current_level = instance.championship.league.level
                
                # Определяем, нужно ли менять лигу
                if current_level == 1 and position >= 15:  # Вылет из высшего дивизиона
                    new_league = League.objects.get(
                        country=team.country,
                        level=2
                    )
                    team.league = new_league
                    team.save()
                elif current_level == 2 and position <= 2:  # Повышение во второй дивизион
                    new_league = League.objects.get(
                        country=team.country,
                        level=1
                    )
                    team.league = new_league
                    team.save()
        except Exception as e:
            raise