from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0015_restore_realtime_broadcast_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='markov_seed',
            field=models.BigIntegerField(
                blank=True,
                help_text='Deterministic seed that ties this match to a Markov stream.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='match',
            name='markov_token',
            field=models.JSONField(
                blank=True,
                help_text='Opaque token returned by the Markov runtime for the next minute.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='match',
            name='markov_coefficients',
            field=models.JSONField(
                blank=True,
                help_text='Attack/defense coefficients snapshot used by the runtime.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='match',
            name='markov_last_summary',
            field=models.JSONField(
                blank=True,
                help_text='Last minute_summary payload with raw events/actions.',
                null=True,
            ),
        ),
    ]
