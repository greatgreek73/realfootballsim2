from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0004_start_minute_at_one'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='started_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='match',
            name='last_minute_update',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
