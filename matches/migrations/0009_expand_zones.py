from django.db import migrations, models


def forwards(apps, schema_editor):
    Match = apps.get_model('matches', 'Match')
    for match in Match.objects.all():
        z = match.current_zone
        mapping = {
            'DEF': 'DEF-C',
            'DM': 'DM-C',
            'MID': 'MID-C',
            'AM': 'AM-C',
            'FWD': 'FWD-C',
        }
        if z in mapping:
            match.current_zone = mapping[z]
            match.save(update_fields=['current_zone'])


def backwards(apps, schema_editor):
    Match = apps.get_model('matches', 'Match')
    for match in Match.objects.all():
        z = match.current_zone
        if z.startswith('DEF'):
            match.current_zone = 'DEF'
        elif z.startswith('DM'):
            match.current_zone = 'DM'
        elif z.startswith('MID'):
            match.current_zone = 'MID'
        elif z.startswith('AM'):
            match.current_zone = 'AM'
        elif z.startswith('FWD'):
            match.current_zone = 'FWD'
        match.save(update_fields=['current_zone'])


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0008_add_dribble_event_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='current_zone',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('GK', 'GK'),
                    ('DEF-L', 'DEF-L'), ('DEF-C', 'DEF-C'), ('DEF-R', 'DEF-R'),
                    ('DM-L', 'DM-L'), ('DM-C', 'DM-C'), ('DM-R', 'DM-R'),
                    ('MID-L', 'MID-L'), ('MID-C', 'MID-C'), ('MID-R', 'MID-R'),
                    ('AM-L', 'AM-L'), ('AM-C', 'AM-C'), ('AM-R', 'AM-R'),
                    ('FWD-L', 'FWD-L'), ('FWD-C', 'FWD-C'), ('FWD-R', 'FWD-R'),
                ],
                default='GK',
                verbose_name='Current Zone',
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]

