import logging
from django.conf import settings
from django_celery_beat.models import PeriodicTask, IntervalSchedule

logger = logging.getLogger(__name__)

def ensure_simulation_schedule():
    """Create or update the periodic task for match simulation."""
    interval, _ = IntervalSchedule.objects.get_or_create(
        every=settings.MATCH_MINUTE_REAL_SECONDS,
        period=IntervalSchedule.SECONDS,
    )
    task, created = PeriodicTask.objects.update_or_create(
        name='simulate-active-matches',
        defaults={
            'task': 'tournaments.simulate_active_matches',
            'interval': interval,
        },
    )
    if not created and task.interval_id != interval.id:
        task.interval = interval
        task.save()
    logger.info(
        "Celery schedule for simulate-active-matches set to %s seconds",
        settings.MATCH_MINUTE_REAL_SECONDS,
    )
