from django.db import migrations, models


def set_initial_minute(apps, schema_editor):
    Match = apps.get_model('matches', 'Match')
    Match.objects.filter(current_minute=0).update(current_minute=1)


class Migration(migrations.Migration):
    dependencies = [
        ('matches', '0003_add_matchevent_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='current_minute',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.RunPython(set_initial_minute, migrations.RunPython.noop),
    ]
