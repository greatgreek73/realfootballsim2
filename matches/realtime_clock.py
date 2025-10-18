import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Optional

from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RealtimeConfig:
    enabled: bool
    seconds_per_game_minute: int
    micro_event_pause_range: tuple[int, int]
    min_events_per_minute: int
    max_events_per_minute: int
    jitter_ms: int

    def with_overrides(self, **overrides) -> "RealtimeConfig":
        data = {
            "enabled": self.enabled,
            "seconds_per_game_minute": self.seconds_per_game_minute,
            "micro_event_pause_range": self.micro_event_pause_range,
            "min_events_per_minute": self.min_events_per_minute,
            "max_events_per_minute": self.max_events_per_minute,
            "jitter_ms": self.jitter_ms,
        }
        data.update(overrides)
        pause_range = data["micro_event_pause_range"]
        if isinstance(pause_range, Iterable) and not isinstance(pause_range, tuple):
            data["micro_event_pause_range"] = tuple(pause_range)
        return RealtimeConfig(**data)


def _range_from_setting(value, default):
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    return default


def get_realtime_config(**overrides) -> RealtimeConfig:
    realtime_cfg = getattr(settings, "MATCH_ENGINE", {}).get("REALTIME", {}) or {}
    base = RealtimeConfig(
        enabled=bool(realtime_cfg.get("ENABLED", False)),
        seconds_per_game_minute=int(realtime_cfg.get("SECONDS_PER_GAME_MINUTE", 60)),
        micro_event_pause_range=_range_from_setting(
            realtime_cfg.get("MICRO_EVENT_PAUSE_RANGE"), (2, 5)
        ),
        min_events_per_minute=int(realtime_cfg.get("MIN_EVENTS_PER_MINUTE", 3)),
        max_events_per_minute=int(realtime_cfg.get("MAX_EVENTS_PER_MINUTE", 8)),
        jitter_ms=int(realtime_cfg.get("JITTER_MS", 200)),
    )
    if overrides:
        return base.with_overrides(**overrides)
    return base


class MatchClock:
    """
    Helper that maps real-time seconds to in-game minutes for a match.
    """

    def __init__(self, match, config: Optional[RealtimeConfig] = None):
        self.match = match
        self.config = config or get_realtime_config()

    @property
    def seconds_per_minute(self) -> int:
        return self.config.seconds_per_game_minute

    def ensure_started(self, now=None):
        """
        Guarantee that realtime_started_at is initialised.
        """
        now = now or timezone.now()
        if not self.match.realtime_started_at:
            logger.debug("Initialising realtime_started_at for match %s", self.match.id)
            self.match.realtime_started_at = now
        return self.match.realtime_started_at

    def deadline(self) -> Optional[datetime]:
        if not self.match.realtime_started_at:
            return None
        return self.match.realtime_started_at + timedelta(seconds=self.seconds_per_minute)

    def elapsed_seconds(self, now=None) -> float:
        if not self.match.realtime_started_at:
            return 0.0
        now = now or timezone.now()
        delta = now - self.match.realtime_started_at
        return max(delta.total_seconds(), 0.0)

    def is_minute_over(self, now=None) -> bool:
        return self.elapsed_seconds(now) >= self.seconds_per_minute

    def seconds_remaining(self, now=None) -> float:
        return max(self.seconds_per_minute - self.elapsed_seconds(now), 0.0)

    def advance_minute_anchor(self, now=None):
        """
        Set realtime_started_at to the provided timestamp (or now) to begin the next minute.
        """
        now = now or timezone.now()
        self.match.realtime_started_at = now
        return self.match.realtime_started_at
