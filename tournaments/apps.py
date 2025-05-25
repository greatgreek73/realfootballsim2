from django.apps import AppConfig

class TournamentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tournaments'
    verbose_name = 'Tournaments Management'

    def ready(self):
        import tournaments.signals
        # Ensure Celery Beat uses the current MATCH_MINUTE_REAL_SECONDS value
        try:
            from .celery_utils import ensure_simulation_schedule
            ensure_simulation_schedule()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f'Failed to update simulation schedule: {e}'
            )
