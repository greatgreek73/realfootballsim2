from django.db.models.signals import post_save
from django.dispatch import receiver
from clubs.models import Club
from tournaments.models import Championship, ChampionshipTeam, ChampionshipMatch
from matches.models import Match
from django.db import transaction
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Club)
def handle_club_creation(sender, instance, created, **kwargs):
    """Обрабатывает создание нового клуба и замещение бота"""
    if not created or instance.is_bot:
        return
        
    try:
        with transaction.atomic():
            # Найти активный сезон и чемпионат для страны клуба
            championship = Championship.objects.select_related('season')\
                .filter(
                    league__country=instance.country,
                    league__level=1,
                    season__is_active=True
                ).first()
                
            if not championship:
                logger.warning(f"No active championship found for club {instance.name}")
                return
                
            # Найти команду-бота для замены
            bot_team = championship.teams.filter(is_bot=True).first()
            if not bot_team:
                logger.warning(f"No bot team found to replace in championship for club {instance.name}")
                return
                
            # Получить статистику бота
            bot_stats = ChampionshipTeam.objects.get(
                championship=championship,
                team=bot_team
            )
            
            # Создать запись для нового клуба с теми же статистическими данными
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
            
            # Удалить бота из чемпионата и базы данных
            bot_stats.delete()
            bot_team.delete()
            
            logger.info(f"Successfully replaced bot team with new club {instance.name}")
            
    except Exception as e:
        logger.error(f"Error handling club creation for {instance.name}: {str(e)}")

@receiver(post_save, sender=Match)
def handle_match_result(sender, instance, **kwargs):
    """Обновляет статистику команд после завершения матча"""
    try:
        # Проверяем, есть ли этот матч в чемпионате
        championship_match = ChampionshipMatch.objects.select_related(
            'championship',
            'match',
            'match__home_team',
            'match__away_team'
        ).filter(match=instance).first()

        if not championship_match:
            logger.debug(f"Match {instance.id} not part of any championship")
            return

        if championship_match.processed:
            logger.debug(f"Match {instance.id} already processed")
            return

        if instance.status != 'finished':
            logger.debug(f"Match {instance.id} not finished yet")
            return

        # Используем retry механизм
        max_attempts = 3
        current_attempt = 0

        while current_attempt < max_attempts:
            try:
                with transaction.atomic():
                    # Блокируем записи статистики для обновления
                    home_stats = ChampionshipTeam.objects.select_for_update().get(
                        championship=championship_match.championship,
                        team=instance.home_team
                    )
                    away_stats = ChampionshipTeam.objects.select_for_update().get(
                        championship=championship_match.championship,
                        team=instance.away_team
                    )

                    # Обновляем общую статистику
                    home_stats.matches_played += 1
                    away_stats.matches_played += 1
                    home_stats.goals_for += instance.home_score
                    home_stats.goals_against += instance.away_score
                    away_stats.goals_for += instance.away_score
                    away_stats.goals_against += instance.home_score

                    # Обновляем результаты (победа/ничья/поражение)
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

                    # Отмечаем матч как обработанный
                    championship_match.processed = True
                    championship_match.save()

                    logger.info(
                        f"Successfully processed match {instance.id}: "
                        f"{instance.home_team} {instance.home_score}-{instance.away_score} {instance.away_team}"
                    )
                    return  # Выходим из функции если все успешно

            except Exception as e:
                current_attempt += 1
                if current_attempt == max_attempts:
                    logger.error(f"Failed to process match {instance.id} after {max_attempts} attempts: {str(e)}")
                    raise
                logger.warning(f"Attempt {current_attempt} failed for match {instance.id}, retrying...")
                import time
                time.sleep(1)  # Ждем секунду перед повторной попыткой

    except Exception as e:
        logger.error(f"Error handling match result for match {instance.id}: {str(e)}")