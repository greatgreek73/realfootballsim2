from django.db import migrations
from django.utils import timezone
from datetime import datetime

def shift_match_dates(apps, schema_editor):
    """Shifts all match dates to start from December 1st, 2024"""
    Match = apps.get_model('matches', 'Match')
    ChampionshipMatch = apps.get_model('tournaments', 'ChampionshipMatch')
    
    for cm in ChampionshipMatch.objects.select_related('match', 'championship'):
        # Используем декабрь вместо ноября
        date = datetime(2024, 12, 1) + timezone.timedelta(days=cm.match_day - 1)
        time = datetime.min.time().replace(hour=18)
        naive_datetime = datetime.combine(date, time)
        match_datetime = timezone.make_aware(naive_datetime)
        
        Match.objects.filter(id=cm.match.id).update(
            datetime=match_datetime
        )

def reverse_shift_match_dates(apps, schema_editor):
    """Reverse the date shift"""
    Match = apps.get_model('matches', 'Match')
    ChampionshipMatch = apps.get_model('tournaments', 'ChampionshipMatch')
    
    for cm in ChampionshipMatch.objects.select_related('match', 'championship'):
        date = datetime(2024, 11, 1) + timezone.timedelta(days=cm.match_day - 1)
        time = datetime.min.time().replace(hour=18)
        naive_datetime = datetime.combine(date, time)
        match_datetime = timezone.make_aware(naive_datetime)
        
        Match.objects.filter(id=cm.match.id).update(
            datetime=match_datetime
        )

class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0008_match_datetime_update'),
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            shift_match_dates,
            reverse_shift_match_dates
        ),
    ]