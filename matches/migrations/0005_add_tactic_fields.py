# Generated manually

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('matches', '0004_match_current_minute'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='home_tactic',
            field=models.CharField(max_length=20, default='balanced'),
        ),
        migrations.AddField(
            model_name='match',
            name='away_tactic',
            field=models.CharField(max_length=20, default='balanced'),
        ),
    ]
