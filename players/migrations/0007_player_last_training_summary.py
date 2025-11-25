from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0006_player_last_trained_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="last_training_summary",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Изменения атрибутов после последней обычной тренировки (3 раза в неделю)",
                verbose_name="Last training changes",
            ),
        ),
    ]
