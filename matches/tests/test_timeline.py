from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from clubs.models import Club
from matches.dispatch import TimelineDispatcher
from matches.models import Match, MatchBroadcastEvent, MatchEvent
from matches.realtime_clock import get_realtime_config
from matches.timeline import build_minute_timeline, persist_broadcast_items
from players.models import Player


class TimelineBuilderTests(TestCase):
    def setUp(self):
        self.home = Club.objects.create(name="Home FC", country="RU")
        self.away = Club.objects.create(name="Away FC", country="DE")
        self.home_players = [
            self._create_player(self.home, first_name="Ivan", last_name="Ivanov", position="Central Midfielder"),
            self._create_player(self.home, first_name="Petr", last_name="Petrov", position="Attacking Midfielder"),
            self._create_player(self.home, first_name="Alex", last_name="Smirnov", position="Center Forward"),
        ]
        self.away_players = [
            self._create_player(self.away, first_name="Sergey", last_name="Sergeev", position="Center Back"),
            self._create_player(self.away, first_name="Igor", last_name="Igorev", position="Goalkeeper"),
        ]

        self.match = Match.objects.create(
            home_team=self.home,
            away_team=self.away,
            datetime=timezone.now(),
            status="in_progress",
            current_minute=1,
            home_lineup={str(idx): player.id for idx, player in enumerate(self.home_players)},
            away_lineup={str(idx): player.id for idx, player in enumerate(self.away_players)},
        )
        self.match.realtime_started_at = timezone.now()
        self.match.save(update_fields=["realtime_started_at"])
        self.config = get_realtime_config().with_overrides(
            enabled=True,
            seconds_per_game_minute=30,
            min_events_per_minute=3,
            max_events_per_minute=6,
            micro_event_pause_range=(2, 3),
            jitter_ms=0,
        )

    def _create_player(self, club, first_name, last_name, position):
        return Player.objects.create(
            first_name=first_name,
            last_name=last_name,
            age=24,
            club=club,
            nationality="RU",
            position=position,
        )

    def test_build_minute_timeline_creates_events_within_limits(self):
        minute_start = timezone.now()
        minute_events = [
            MatchEvent.objects.create(
                match=self.match,
                minute=self.match.current_minute,
                event_type="pass",
                player=self.home_players[0],
                related_player=self.home_players[1],
                description="Ivanov коротко играет на Петрова",
            ),
            MatchEvent.objects.create(
                match=self.match,
                minute=self.match.current_minute,
                event_type="goal",
                player=self.home_players[2],
                description="Смирнов вколачивает в сетку!",
            ),
        ]

        items = build_minute_timeline(
            self.match,
            config=self.config,
            minute_events=minute_events,
            minute_start=minute_start,
        )

        self.assertGreaterEqual(len(items), self.config.min_events_per_minute)
        self.assertLessEqual(len(items), self.config.max_events_per_minute)

        for item in items:
            self.assertGreaterEqual(item.scheduled_at, minute_start)
            self.assertLessEqual(
                item.scheduled_at,
                minute_start + timedelta(seconds=self.config.seconds_per_game_minute),
            )

        persist_broadcast_items(self.match, self.match.current_minute, items)
        self.assertEqual(MatchBroadcastEvent.objects.filter(match=self.match).count(), len(items))

    def test_persist_is_idempotent(self):
        minute_start = timezone.now()
        items = build_minute_timeline(
            self.match,
            config=self.config,
            minute_events=[],
            minute_start=minute_start,
        )

        persist_broadcast_items(self.match, self.match.current_minute, items)
        persist_broadcast_items(self.match, self.match.current_minute, items)
        self.assertEqual(
            MatchBroadcastEvent.objects.filter(match=self.match).count(),
            len(items),
        )

    def test_dispatcher_marks_events_sent(self):
        minute_start = timezone.now() - timedelta(seconds=30)
        items = build_minute_timeline(
            self.match,
            config=self.config,
            minute_events=[],
            minute_start=minute_start,
        )
        persist_broadcast_items(self.match, self.match.current_minute, items)

        dispatcher = TimelineDispatcher(self.match.id)
        sent = dispatcher.dispatch_ready(now=timezone.now() + timedelta(seconds=5))
        self.assertEqual(sent, len(items))
        self.assertFalse(
            MatchBroadcastEvent.objects.filter(
                match=self.match, status=MatchBroadcastEvent.STATUS_PENDING
            ).exists()
        )
