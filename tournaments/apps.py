from django.apps import AppConfig

class TournamentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tournaments'
    verbose_name = 'Tournaments Management'

    def ready(self):
        import tournaments.signals
        # Ensure Celery Beat uses the current MATCH_MINUTE_REAL_SECONDS value
        try:
            import sys
            from django.db import connection
            if (
                'migrate' in sys.argv
                or 'makemigrations' in sys.argv
                or 'django_celery_beat_intervalschedule'
                not in connection.introspection.table_names()
            ):
                return

            from .celery_utils import ensure_simulation_schedule
            ensure_simulation_schedule()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f'Failed to update simulation schedule: {e}'
            )