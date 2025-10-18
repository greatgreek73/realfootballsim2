from django.db import migrations, models


SQL_ADD_REALTIME_STARTED_AT = """
ALTER TABLE matches_match
ADD COLUMN IF NOT EXISTS realtime_started_at TIMESTAMPTZ NULL;
"""

SQL_DROP_REALTIME_STARTED_AT = """
ALTER TABLE matches_match
DROP COLUMN IF EXISTS realtime_started_at;
"""

SQL_ADD_MINUTE_BUILDING = """
ALTER TABLE matches_match
ADD COLUMN IF NOT EXISTS minute_building BOOLEAN NOT NULL DEFAULT FALSE;
"""

SQL_DROP_MINUTE_BUILDING = """
ALTER TABLE matches_match
DROP COLUMN IF EXISTS minute_building;
"""

SQL_ADD_LAST_BROADCAST = """
ALTER TABLE matches_match
ADD COLUMN IF NOT EXISTS match_last_broadcast_minute INTEGER NOT NULL DEFAULT 0;
"""

SQL_DROP_LAST_BROADCAST = """
ALTER TABLE matches_match
DROP COLUMN IF EXISTS match_last_broadcast_minute;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0014_remove_match_minute_building_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(SQL_ADD_REALTIME_STARTED_AT, SQL_DROP_REALTIME_STARTED_AT),
                migrations.RunSQL(SQL_ADD_MINUTE_BUILDING, SQL_DROP_MINUTE_BUILDING),
                migrations.RunSQL(SQL_ADD_LAST_BROADCAST, SQL_DROP_LAST_BROADCAST),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='match',
                    name='realtime_started_at',
                    field=models.DateTimeField(
                        blank=True,
                        null=True,
                        db_index=True,
                        help_text='Timestamp when the current broadcast minute began.',
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
                migrations.AddField(
                    model_name='match',
                    name='realtime_last_broadcast_minute',
                    field=models.PositiveIntegerField(
                        db_column='match_last_broadcast_minute',
                        default=0,
                        help_text='Last game minute that was expanded into a broadcast timeline.',
                    ),
                ),
            ],
        ),
    ]
