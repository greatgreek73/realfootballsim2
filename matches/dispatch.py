import logging
from typing import Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from matches.models import MatchBroadcastEvent

logger = logging.getLogger(__name__)


class TimelineDispatcher:
    """
    Periodically polls pending broadcast events and sends them through Channels.
    """

    def __init__(self, match_id: int, *, channel_layer=None):
        self.match_id = match_id
        self.channel_layer = channel_layer or get_channel_layer()
        if self.channel_layer is None:
            logger.warning("Channel layer is not configured; dispatcher will not send events.")

    def dispatch_ready(self, *, now=None, batch_size: int = 20) -> int:
        """
        Send all pending events whose scheduled_at is in the past.
        Returns the number of events sent.
        """
        if self.channel_layer is None:
            return 0
        now = now or timezone.now()

        pending = list(
            MatchBroadcastEvent.objects.filter(
                match_id=self.match_id,
                status=MatchBroadcastEvent.STATUS_PENDING,
                scheduled_at__lte=now,
            ).order_by("scheduled_at", "idx_in_minute")[:batch_size]
        )

        if not pending:
            return 0

        sent_count = 0
        for event in pending:
            payload = event.payload_json or {}
            commentary_message = {"type": "commentary_line", "data": payload}
            async_to_sync(self.channel_layer.group_send)(f"match_{self.match_id}", commentary_message)
            if payload.get("score_update"):
                score_message = {"type": "score_update", "data": payload["score_update"]}
                async_to_sync(self.channel_layer.group_send)(f"match_{self.match_id}", score_message)
            if payload.get("possession_update"):
                possession_message = {"type": "possession_update", "data": payload["possession_update"]}
                async_to_sync(self.channel_layer.group_send)(f"match_{self.match_id}", possession_message)
            event.mark_sent(now)
            sent_count += 1
            logger.debug(
                "Dispatched commentary event match=%s minute=%s idx=%s payload=%s",
                self.match_id,
                event.game_minute,
                event.idx_in_minute,
                payload.get("kind"),
            )
        return sent_count

    def has_pending(self) -> bool:
        return MatchBroadcastEvent.objects.filter(
            match_id=self.match_id,
            status=MatchBroadcastEvent.STATUS_PENDING,
        ).exists()

    def resend_due(self, *, now=None) -> int:
        """
        Replays unsent events that should have been sent already (used after restart).
        """
        return self.dispatch_ready(now=now)

