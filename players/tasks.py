import logging
from typing import Optional
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import Max
from django.core.cache import cache
from datetime import datetime, date, time, timedelta
import pytz
from django.conf import settings

from .training_logic import conduct_all_teams_training

logger = logging.getLogger("player_training")


TRAINING_CACHE_KEY = "players:last_training_run"
MAX_CATCHUP_DAYS = 6

def _get_training_timezone():
    tz_name = getattr(settings, "TRAINING_TIMEZONE", "CET")
    try:
        return pytz.timezone(tz_name)
    except Exception:
        return pytz.timezone("CET")

def _get_training_days():
    return getattr(settings, "TRAINING_DAY_LIST", None) or [0, 2, 4]

def _build_training_timestamp(run_for_date=None):
    tz = _get_training_timezone()
    if run_for_date:
        if isinstance(run_for_date, str):
            run_for_date = date.fromisoformat(run_for_date)
        if isinstance(run_for_date, datetime):
            run_for_date = run_for_date.date()
        local_dt = tz.localize(
            datetime.combine(
                run_for_date,
                time(
                    hour=getattr(settings, "TRAINING_CRON_HOUR", 11),
                    minute=getattr(settings, "TRAINING_CRON_MINUTE", 0),
                ),
            )
        )
        return local_dt.astimezone(timezone.utc)
    return timezone.now()

def _remember_training_run(at_dt):
    try:
        cache.set(TRAINING_CACHE_KEY, at_dt.isoformat())
    except Exception as e:
        logger.warning(f"[training] Failed to persist training timestamp: {e}")

def _get_last_training_run_local(tz):
    raw = cache.get(TRAINING_CACHE_KEY)
    dt = None

    if raw:
        try:
            dt = datetime.fromisoformat(raw)
        except Exception:
            dt = None

    if dt is None:
        try:
            from .models import Player

            dt = Player.objects.aggregate(last=Max('last_trained_at')).get('last')
        except Exception as e:
            logger.warning("[training] Could not read last_trained_at: %s", e)
            dt = None

    if dt is None:
        return None

    if timezone.is_naive(dt):
        dt = tz.localize(dt)

    try:
        cache.set(TRAINING_CACHE_KEY, dt.isoformat())
    except Exception:
        pass

    return dt.astimezone(tz)


def _collect_missed_training_dates(last_run_local, now_local, training_days):
    if last_run_local:
        cursor = last_run_local.date() + timedelta(days=1)
    else:
        cursor = now_local.date()
    today = now_local.date()
    missed = []
    while cursor <= today and len(missed) < MAX_CATCHUP_DAYS:
        if cursor.weekday() in training_days:
            missed.append(cursor)
        cursor += timedelta(days=1)
    return missed

@shared_task(name='players.conduct_scheduled_training', bind=True)
def conduct_scheduled_training(self, run_for_date: Optional[str] = None):
    """
    Scheduled team training for all clubs.
    Defaults to Mon/Wed/Fri at 12:00 CET.
    """
    run_ts = _build_training_timestamp(run_for_date)
    logger.info(
        "[conduct_scheduled_training] Starting training at %s (run_for_date=%s)",
        run_ts,
        run_for_date,
    )

    try:
        with transaction.atomic():
            stats = conduct_all_teams_training(when=run_ts)

            logger.info(
                "[training] Summary: teams=%s players=%s improvements=%s bloom=%s errors=%s",
                stats.get('teams_trained'),
                stats.get('players_trained'),
                stats.get('total_improvements'),
                stats.get('players_in_bloom'),
                stats.get('errors'),
            )

            _remember_training_run(run_ts)

            return {
                'status': 'success',
                'timestamp': run_ts.isoformat(),
                'stats': stats,
            }

    except Exception as e:
        logger.error("[training] Failed to run training: %s", e)
        return {
            'status': 'error',
            'timestamp': run_ts.isoformat(),
            'error': str(e),
        }


@shared_task(name='players.advance_player_seasons', bind=True)
def advance_player_seasons(self):
    """
    Продвигает сезоны расцвета игроков.
    Запускается в начале каждого нового сезона.
    """
    from .models import Player
    
    now = timezone.now()
    logger.info(f"📅 [advance_player_seasons] Продвижение сезонов игроков в {now}")
    
    stats = {
        'players_processed': 0,
        'blooms_started': 0,
        'blooms_ended': 0,
        'errors': 0
    }
    
    try:
        with transaction.atomic():
            players = Player.objects.all()
            
            for player in players:
                try:
                    stats['players_processed'] += 1
                    
                    # Проверяем, нужно ли запустить расцвет
                    if player.should_start_bloom():
                        player.start_bloom()
                        stats['blooms_started'] += 1
                        logger.info(
                            f"🌟 Начат расцвет игрока {player.full_name} "
                            f"({player.bloom_type}, возраст {player.age})"
                        )
                    
                    # Продвигаем существующий расцвет
                    if player.is_in_bloom:
                        old_seasons = player.bloom_seasons_left
                        player.advance_bloom_season()
                        
                        if player.bloom_seasons_left == 0:
                            stats['blooms_ended'] += 1
                            logger.info(
                                f"🏁 Завершен расцвет игрока {player.full_name} "
                                f"({player.bloom_type})"
                            )
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка при обработке игрока {player.id}: {e}")
                    stats['errors'] += 1
            
            logger.info(
                f"✅ Сезоны игроков продвинуты. Статистика: "
                f"Обработано: {stats['players_processed']}, "
                f"Расцветов начато: {stats['blooms_started']}, "
                f"Расцветов завершено: {stats['blooms_ended']}, "
                f"Ошибок: {stats['errors']}"
            )
            
            return {
                'status': 'success',
                'timestamp': now.isoformat(),
                'stats': stats
            }
            
    except Exception as e:
        logger.error(f"❌ Ошибка при продвижении сезонов: {e}")
        return {
            'status': 'error',
            'timestamp': now.isoformat(),
            'error': str(e)
        }


def is_training_day():
    """
    Return True if today is a training day in the configured training TZ.
    """
    tz = _get_training_timezone()
    now_local = timezone.now().astimezone(tz)
    return now_local.weekday() in _get_training_days()


@shared_task(name='players.check_training_schedule', bind=True)
def check_training_schedule(self):
    """
    Decide if training should run today and queue catch-ups for missed training days (up to MAX_CATCHUP_DAYS).
    """
    tz = _get_training_timezone()
    now_local = timezone.now().astimezone(tz)
    training_days = _get_training_days()
    last_run_local = _get_last_training_run_local(tz)

    missed_dates = _collect_missed_training_dates(last_run_local, now_local, training_days)

    if not missed_dates:
        logger.info(
            "[training] No trainings to run. today_weekday=%s last_run=%s",
            now_local.weekday(),
            last_run_local,
        )
        return {
            'status': 'skipped',
            'reason': 'Not a training day or already trained',
            'timestamp': timezone.now().isoformat(),
            'last_run': last_run_local.isoformat() if last_run_local else None,
        }

    task_ids = []
    for idx, day in enumerate(missed_dates, 1):
        logger.info(
            "[training] Queue training for %s (%s/%s missed)",
            day,
            idx,
            len(missed_dates),
        )
        async_res = conduct_scheduled_training.delay(run_for_date=day.isoformat())
        task_ids.append(str(async_res))

    return {
        'status': 'queued',
        'dates': [d.isoformat() for d in missed_dates],
        'tasks': task_ids,
        'timestamp': timezone.now().isoformat(),
    }
