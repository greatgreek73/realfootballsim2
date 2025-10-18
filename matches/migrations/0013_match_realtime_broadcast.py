from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0012_add_personality_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='realtime_started_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Timestamp when the current broadcast minute began.',
                null=True,
                db_index=True,
            ),
        ),
        migrations.AddField(
            model_name='match',
            name='realtime_last_broadcast_minute',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Last game minute that was expanded into a broadcast timeline.',
            ),
        ),
        migrations.AddField(
            model_name='match',
            name='minute_building',
            field=models.BooleanField(
                default=False,
                help_text='Internal lock that prevents concurrent timeline generation.',
            ),
        ),
        migrations.CreateModel(
            name='MatchBroadcastEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_minute', models.PositiveIntegerField(db_index=True)),
                ('idx_in_minute', models.PositiveIntegerField()),
                ('payload_json', models.JSONField()),
                ('scheduled_at', models.DateTimeField(db_index=True)),
                ('sent_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('skipped', 'Skipped')], db_index=True, default='pending', max_length=8)),
                ('idempotency_key', models.CharField(max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('match', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='broadcast_events', to='matches.match')),
            ],
            options={
                'ordering': ('match', 'game_minute', 'idx_in_minute'),
                'unique_together': {('match', 'game_minute', 'idx_in_minute')},
            },
        ),
        migrations.AddIndex(
            model_name='matchbroadcastevent',
            index=models.Index(fields=['match', 'game_minute', 'status'], name='matches_mat_match_i_348213_idx'),
        ),
        migrations.AddIndex(
            model_name='matchbroadcastevent',
            index=models.Index(fields=['match', 'scheduled_at'], name='matches_mat_match_s_348214_idx'),
        ),
    ]

