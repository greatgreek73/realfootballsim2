from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0005_match_real_time_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='waiting_for_next_minute',
            field=models.BooleanField(default=False),
        ),
    ]
