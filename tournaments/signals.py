from django.db.models.signals import post_save
from django.dispatch import receiver
from clubs.models import Club
from tournaments.models import Championship, ChampionshipTeam, ChampionshipMatch
from matches.models import Match
from django.db import transaction
from django.db.models import Q
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

def update_matches_for_replaced_team(championship, old_team_id, new_team):
    """
    Обновляет все матчи, заменяя old_team на new_team
    """
    try:
        with transaction.atomic():
            logger.info(
                f"Starting match update: replacing team {old_team_id} with {new_team.name} "
                f"in championship {championship}"
            )

            # Сначала получаем все матчи бота для анализа
            bot_matches = Match.objects.filter(
                championshipmatch__championship=championship
            ).filter(
                Q(home_team_id=old_team_id) | Q(away_team_id=old_team_id)
            ).select_related(
                'championshipmatch',
                'home_team',
                'away_team'
            ).order_by('championshipmatch__round')

            logger.info(f"Found {bot_matches.count()} matches to update")

            # Группируем матчи по турам для проверки
            matches_by_round = {}
            for match in bot_matches:
                round_num = match.championshipmatch.round
                if round_num not in matches_by_round:
                    matches_by_round[round_num] = []
                matches_by_round[round_num].append(match)

            # Анализируем матчи бота
            logger.info(f"Analyzing matches by round:")
            for round_num, round_matches in matches_by_round.items():
                logger.info(f"Round {round_num}:")
                for match in round_matches:
                    logger.info(f"- {match.home_team.name} vs {match.away_team.name}")

            # Проверяем противников бота
            opponents = set()
            opponent_matches = {}
            for match in bot_matches:
                opponent = match.away_team if match.home_team_id == old_team_id else match.home_team
                opponents.add(opponent.id)
                if opponent.id not in opponent_matches:
                    opponent_matches[opponent.id] = []
                opponent_matches[opponent.id].append(match)

            logger.info(f"Found {len(opponents)} unique opponents")
            for opponent_id, matches in opponent_matches.items():
                logger.info(f"Games against opponent {opponent_id}: {len(matches)}")

            # Обновляем матчи, проверяя правильность
            updated_count = 0
            unique_opponents = set()  # Для проверки уникальности противников
            
            for match in bot_matches:
                before_update = f"{match.home_team.name} vs {match.away_team.name}"

                # Получаем противника в этом матче
                opponent = match.away_team if match.home_team_id == old_team_id else match.home_team
                unique_opponents.add(opponent.id)
                
                # Сохраняем информацию о домашней/гостевой игре
                was_home = match.home_team_id == old_team_id

                # Обновляем команду в матче
                if was_home:
                    match.home_team = new_team
                else:
                    match.away_team = new_team

                match.save()
                updated_count += 1

                logger.info(
                    f"Updated match {match.id} (Round {match.championshipmatch.round}): "
                    f"{before_update} -> {match.home_team.name} vs {match.away_team.name}"
                )

            # Финальные проверки
            logger.info(f"Update completed:")
            logger.info(f"- Total matches updated: {updated_count}")
            logger.info(f"- Unique opponents: {len(unique_opponents)}")

            # Проверяем итоговое распределение
            final_matches = Match.objects.filter(
                championshipmatch__championship=championship,
                home_team=new_team
            ).count()
            logger.info(f"Final home matches: {final_matches}")

            away_matches = Match.objects.filter(
                championshipmatch__championship=championship,
                away_team=new_team
            ).count()
            logger.info(f"Final away matches: {away_matches}")

            if len(unique_opponents) < 2:
                raise ValueError(
                    f"Error: team has only {len(unique_opponents)} opponents. "
                    f"Something is wrong with the schedule."
                )

            return updated_count

    except Exception as e:
        logger.error(f"Error updating matches for team {new_team.name}: {str(e)}")
        raise

@receiver(post_save, sender=Club)
def handle_club_creation(sender, instance, created, **kwargs):
    """Обрабатывает создание нового клуба и замещение бота"""
    if not created or instance.is_bot:
        return
        
    try:
        with transaction.atomic():
            logger.info(f"Processing new club creation: {instance.name}")
            
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
            
            logger.info(f"Found championship: {championship}")

            # Проверяем, не добавлен ли уже клуб в чемпионат
            if championship.teams.filter(id=instance.id).exists():
                logger.info(f"Club {instance.name} is already in championship")
                return
                
            # Найти команду-бота для замены
            bot_team = championship.teams.filter(is_bot=True).first()
            if not bot_team:
                logger.warning(f"No bot team found to replace in championship for club {instance.name}")
                return
                
            logger.info(f"Found bot team to replace: {bot_team.name} (ID: {bot_team.id})")
            
            # Сохраняем ID бота перед удалением
            bot_team_id = bot_team.id
                
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
            
            logger.info(f"Created championship team record for {instance.name}")
            
            # Обновить все матчи, заменив бота на новый клуб
            updated_matches = update_matches_for_replaced_team(
                championship=championship,
                old_team_id=bot_team_id,
                new_team=instance
            )
            logger.info(f"Updated {updated_matches} matches for team {instance.name}")
            
            # Удалить бота из чемпионата и базы данных
            bot_stats.delete()
            bot_team.delete()
            logger.info(f"Deleted bot team {bot_team.name} (ID: {bot_team_id})")
            
            logger.info(f"Successfully replaced bot team with new club {instance.name}")
            
    except Exception as e:
        logger.error(f"Error handling club creation for {instance.name}: {str(e)}")
        raise  # Добавляем raise для лучшей диагностики ошибок

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