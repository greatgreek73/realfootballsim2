from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('matches', '0007_merge_20250529_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchevent',
            name='event_type',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('goal', 'Goal'),
                    ('pass', 'Pass'),
                    ('dribble', 'Dribble'),
                    ('interception', 'Interception'),
                    ('counterattack', 'Counterattack'),
                    ('shot_miss', 'Shot Miss'),
                    ('foul', 'Foul'),
                    ('injury_concern', 'Injury Concern'),
                    ('info', 'Info'),
                    ('match_start', 'Match Start'),
                    ('half_time', 'Half Time'),
                    ('match_end', 'Match End'),
                    ('match_paused', 'Match Paused'),
                    ('yellow_card', 'Yellow Card'),
                    ('red_card', 'Red Card'),
                    ('substitution', 'Substitution'),
                ],
                db_index=True,
            ),
        ),
    ]
