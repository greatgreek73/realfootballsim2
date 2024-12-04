from django.db import migrations
from datetime import datetime, timedelta
from django.utils import timezone

def set_datetime_for_matches(apps, schema_editor):
    """Update datetime field for all matches based on their championship data"""
    Match = apps.get_model('matches', 'Match')
    ChampionshipMatch = apps.get_model('tournaments', 'ChampionshipMatch')
    
    for cm in ChampionshipMatch.objects.select_related('match', 'championship'):
        date = cm.championship.start_date + timedelta(days=cm.match_day - 1)
        time = datetime.min.time().replace(hour=18)
        naive_datetime = datetime.combine(date, time)
        match_datetime = timezone.make_aware(naive_datetime)
        
        Match.objects.filter(id=cm.match.id).update(
            datetime=match_datetime
        )

def reverse_datetime_update(apps, schema_editor):
    """Reverse the datetime update"""
    Match = apps.get_model('matches', 'Match')
    Match.objects.all().update(datetime=None)

class Migration(migrations.Migration):
    dependencies = [
        ('matches', '0007_remove_match_date_match_datetime_match_processed_and_more'),
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            set_datetime_for_matches,
            reverse_datetime_update
        ),
    ]