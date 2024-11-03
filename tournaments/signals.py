from django.db.models.signals import post_save
from django.dispatch import receiver
from clubs.models import Club
from tournaments.models import Championship, ChampionshipTeam
from django.db import transaction

@receiver(post_save, sender=Club)
def handle_club_creation(sender, instance, created, **kwargs):
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
                return
                
            # Найти команду-бота для замены
            bot_team = championship.teams.filter(is_bot=True).first()
            if not bot_team:
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
            
    except Exception as e:
        print(f"Error handling club creation: {e}")