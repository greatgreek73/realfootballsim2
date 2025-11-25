from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0005_player_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="last_trained_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Last regular training at"),
        ),
    ]

