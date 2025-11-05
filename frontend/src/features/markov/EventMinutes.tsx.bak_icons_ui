import { Box, Divider, Stack, Typography } from "@mui/material";

import type { MatchEvent } from "@/api/matches";

function formatTimestamp(value: string | null) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(date);
}

export function EventMinutes({ events }: { events: MatchEvent[] }) {
  if (!events?.length) {
    return (
      <Typography variant="body2" color="text.secondary">
        No events recorded yet.
      </Typography>
    );
  }

  const byMinute = new Map<number, MatchEvent[]>();
  for (const ev of events) {
    const m = Number(ev.minute ?? 0);
    if (!byMinute.has(m)) byMinute.set(m, []);
    byMinute.get(m)!.push(ev);
  }

  const minutes = Array.from(byMinute.keys()).sort((a, b) => b - a);

  return (
    <Stack spacing={1.5}>
      {minutes.map((minute) => {
        const list = byMinute.get(minute)!;

        return (
          <Box
            key={`minute-${minute}`}
            sx={{ border: 1, borderColor: "divider", borderRadius: 2, overflow: "hidden" }}
          >
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={1}
              justifyContent="space-between"
              sx={{ p: 2, pb: 1, backgroundColor: "action.hover" }}
            >
              <Typography variant="subtitle2">{minute}'</Typography>
              <Typography variant="caption" color="text.secondary">
                {list.length} {list.length === 1 ? "event" : "events"}
              </Typography>
            </Stack>
            <Divider />

            <Stack spacing={1.5} sx={{ p: 2 }}>
              {list.map((event) => (
                <Box key={event.id}>
                  <Stack direction={{ xs: "column", sm: "row" }} spacing={1} justifyContent="space-between">
                    <Typography variant="subtitle2">
                      {event.type_label ? `${event.type_label}` : "Event"}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatTimestamp(event.timestamp)}
                    </Typography>
                  </Stack>
                  {event.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {event.description}
                    </Typography>
                  )}
                  <Typography variant="caption" color="text.secondary">
                    {event.player?.name ?? "-"}
                    {event.related_player?.name ? ` -> ${event.related_player.name}` : ""}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Box>
        );
      })}
    </Stack>
  );
}
