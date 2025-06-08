from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('matches', '0009_expand_zones'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='home_momentum',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='away_momentum',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='home_pass_streak',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='away_pass_streak',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
