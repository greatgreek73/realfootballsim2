import asyncio
import logging
from typing import Optional

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from matches.dispatch import TimelineDispatcher
from matches.models import Match, MatchBroadcastEvent
from matches.realtime_clock import MatchClock, RealtimeConfig, get_realtime_config
from matches.timeline import build_and_store_minute_timeline
from matches.utils import advance_match_minute


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run minute-by-minute real-time broadcast for a match."

    def add_arguments(self, parser):
        parser.add_argument("--match", type=int, required=True, help="Match ID to broadcast.")
        parser.add_argument(
            "--speed",
            type=int,
            help="Override seconds per in-game minute (e.g. 10 for accelerated tests).",
        )
        parser.add_argument(
            "--tick",
            type=float,
            default=0.25,
            help="Polling interval in seconds for dispatcher loop.",
        )
        parser.add_argument(
            "--max-actions",
            type=int,
            default=8,
            help="Maximum simulation actions per minute when generating timeline.",
        )

    def handle(self, *args, **options):
        match_id = options["match"]
        try:
            match = Match.objects.get(pk=match_id)
        except Match.DoesNotExist as exc:
            raise CommandError(f"Match {match_id} not found") from exc

        config = get_realtime_config()
        if not config.enabled:
            self.stdout.write(self.style.WARNING("Realtime mode disabled in settings."))
        if options.get("speed"):
            config = config.with_overrides(seconds_per_game_minute=int(options["speed"]))

        tick = max(0.1, float(options["tick"]))
        max_actions = max(1, int(options["max_actions"]))

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting realtime broadcast for match {match_id} "
                f"(seconds_per_minute={config.seconds_per_game_minute}, tick={tick})"
            )
        )

        asyncio.run(self._run_loop(match_id, config, tick=tick, max_actions=max_actions))

    async def _run_loop(self, match_id: int, config: RealtimeConfig, *, tick: float, max_actions: int):
        dispatcher = TimelineDispatcher(match_id)
        await sync_to_async(self._prime_pending)(match_id)
        active = True
        while active:
            active = await sync_to_async(self._process_tick)(match_id, config, max_actions)
            await sync_to_async(dispatcher.dispatch_ready)(now=timezone.now())
            await asyncio.sleep(tick)

    def _prime_pending(self, match_id: int):
        """
        On restart, immediately mark overdue events for dispatch.
        """
        dispatcher = TimelineDispatcher(match_id)
        dispatcher.dispatch_ready(now=timezone.now())

    def _process_tick(self, match_id: int, config: RealtimeConfig, max_actions: int) -> bool:
        now = timezone.now()
        to_build = False
        minute_start = now
        minute_to_build: Optional[int] = None

        with transaction.atomic():
            match = (
                Match.objects.select_for_update()
                .select_related("home_team", "away_team")
                .get(pk=match_id)
            )
            if match.status not in ("in_progress", "paused"):
                logger.info("Match %s not in active state (%s); stopping loop.", match_id, match.status)
                return False

            clock = MatchClock(match, config=config)
            minute_start = clock.ensure_started(now)
            current_minute = match.current_minute
            timeline_exists = MatchBroadcastEvent.objects.filter(
                match=match,
                game_minute=current_minute,
            ).exists()

            if not timeline_exists and match.realtime_last_broadcast_minute < current_minute:
                # Mark timeline as building to prevent parallel tasks.
                match.minute_building = True
                match.waiting_for_next_minute = True
                match.realtime_started_at = minute_start
                match.save(
                    update_fields=["minute_building", "waiting_for_next_minute", "realtime_started_at"]
                )
                to_build = True
                minute_to_build = current_minute

        if to_build:
            logger.debug("Building timeline for match %s minute %s", match_id, minute_to_build)
            build_and_store_minute_timeline(
                match_id,
                config=config,
                minute_start=minute_start,
                max_actions=max_actions,
            )

        with transaction.atomic():
            match = (
                Match.objects.select_for_update()
                .select_related("home_team", "away_team")
                .get(pk=match_id)
            )
            current_minute = match.current_minute
            clock = MatchClock(match, config=config)
            deadline = clock.deadline()
            pending_exists = MatchBroadcastEvent.objects.filter(
                match=match,
                game_minute=current_minute,
                status=MatchBroadcastEvent.STATUS_PENDING,
            ).exists()

            if deadline and timezone.now() >= deadline and not pending_exists:
                logger.debug("Advancing match %s from minute %s", match_id, current_minute)
                advance_match_minute(match, to_minute=current_minute + 1)
                clock.advance_minute_anchor()
                match.waiting_for_next_minute = False
                match.save(update_fields=["realtime_started_at", "waiting_for_next_minute"])

            return match.status in ("in_progress", "paused")
