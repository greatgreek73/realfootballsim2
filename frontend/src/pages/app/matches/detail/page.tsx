import { useEffect, useMemo, useState } from "react";
import { Link as RouterLink, useParams } from "react-router-dom";

import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  Link,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

import {
  fetchMatchDetail,
  fetchMatchEvents,
  MatchDetail,
  MatchEvent,
  MatchEventsResponse,
  MatchStatus,
} from "@/api/matches";

const STATUS_COLOR: Record<MatchStatus, "default" | "info" | "warning" | "success" | "error"> = {
  scheduled: "info",
  in_progress: "warning",
  paused: "warning",
  finished: "success",
  cancelled: "default",
  error: "error",
};

const DATE_FORMATTER = new Intl.DateTimeFormat(undefined, {
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

function formatDate(value: string | null) {
  if (!value) return "TBD";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return DATE_FORMATTER.format(date);
}

type LineupEntry = {
  slot: string;
  slotLabel: string;
  playerName: string;
  position?: string;
};

const normalizeMatchLineup = (raw: unknown): LineupEntry[] => {
  if (!raw || typeof raw !== "object") return [];
  const source = "lineup" in (raw as any) ? (raw as any).lineup : raw;
  if (!source || typeof source !== "object") return [];

  return Object.entries(source).map(([slot, value]) => {
    const data = value as any;
    const slotLabel = data?.slotLabel || data?.label || `Slot ${slot}`;
    const playerId = data?.playerId ?? data?.player ?? data;
    const playerName =
      data?.playerName ||
      data?.name ||
      data?.player_name ||
      data?.full_name ||
      data?.displayName ||
      (playerId !== undefined && playerId !== null ? String(playerId) : "No player");
    const position = data?.playerPosition || data?.position;
    return {
      slot: String(slot),
      slotLabel: String(slotLabel),
      playerName: String(playerName),
      position: position ? String(position) : undefined,
    };
  });
};

export default function MatchDetailPage() {
  const { matchId: matchIdParam } = useParams<{ matchId: string }>();
  const matchId = Number(matchIdParam);

  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [events, setEvents] = useState<MatchEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [eventsError, setEventsError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!Number.isFinite(matchId)) {
      setError("Invalid match id");
      setLoading(false);
      return;
    }

    async function load(id: number) {
      try {
        setLoading(true);
        setError(null);
        const detail = await fetchMatchDetail(id);
        if (!cancelled) setMatch(detail);
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load match");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load(matchId);
    return () => {
      cancelled = true;
    };
  }, [matchId]);

  useEffect(() => {
    let cancelled = false;
    if (!Number.isFinite(matchId)) return;

    async function loadEvents(id: number) {
      try {
        setEventsLoading(true);
        setEventsError(null);
        const response: MatchEventsResponse = await fetchMatchEvents(id);
        if (!cancelled) setEvents(response.events);
      } catch (e: any) {
        if (!cancelled) setEventsError(e?.message ?? "Failed to load events");
      } finally {
        if (!cancelled) setEventsLoading(false);
      }
    }

    loadEvents(matchId);
    return () => {
      cancelled = true;
    };
  }, [matchId]);

  const homeLineup = useMemo(() => normalizeMatchLineup(match?.home?.lineup), [match?.home?.lineup]);
  const awayLineup = useMemo(() => normalizeMatchLineup(match?.away?.lineup), [match?.away?.lineup]);

  return (
    <Box sx={{ p: { xs: 2, sm: 4 } }}>
      <Stack spacing={3}>
        <Stack direction="row" spacing={1} alignItems="center">
          <IconButton component={RouterLink} to="/matches" color="primary">
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h1" component="h1" className="mb-0">
            Match Details
          </Typography>
        </Stack>

        {error && <Alert severity="error">{error}</Alert>}

        {loading ? (
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", p: 8 }}>
            <CircularProgress />
          </Box>
        ) : match ? (
          <>
            <Card>
              <CardContent>
                <Grid container spacing={3} alignItems="center">
                  <Grid size={{ xs: 12, md: "grow" }}>
                    <Stack spacing={1}>
                      <Typography variant="h4">
                        {match.home.name} vs {match.away.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {match.competition
                          ? `${match.competition.name ?? "Competition"} - ${match.competition.season ?? ""}`
                          : "Friendly match"}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(match.datetime)}
                      </Typography>
                    </Stack>
                  </Grid>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Stack spacing={1} alignItems="flex-end">
                      <Typography variant="h2">
                        {match.score.home} : {match.score.away}
                      </Typography>
                      <Chip label={match.status_label} color={STATUS_COLOR[match.status]} variant="outlined" size="medium" />
                      <Typography variant="caption" color="text.secondary">
                        Current minute: {match.current_minute}
                      </Typography>
                    </Stack>
                  </Grid>
                </Grid>

                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 2 }}>
                  <Link component={RouterLink} to={`/matches/${match.id}/live`} underline="hover">
                    Open live view
                  </Link>
                </Stack>

                <Divider sx={{ my: 3 }} />

                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Typography variant="subtitle1">Home</Typography>
                    <Typography variant="body1" fontWeight={600} className="mb-1">
                      {match.home.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tactic: {match.home.tactic ?? "-"}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Typography variant="subtitle1">Away</Typography>
                    <Typography variant="body1" fontWeight={600} className="mb-1">
                      {match.away.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tactic: {match.away.tactic ?? "-"}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" className="mb-2">
                      Home lineup
                    </Typography>
                    <Typography variant="body2" color="text.secondary" className="mb-2">
                      {match.home.name} — tactic: {match.home.tactic ?? "-"}
                    </Typography>
                    {homeLineup.length === 0 ? (
                      <Typography variant="body2" color="text.secondary">
                        Нет данных о составе.
                      </Typography>
                    ) : (
                      <List dense>
                        {homeLineup.map((item) => (
                          <ListItem key={`${item.slot}-${item.playerName}`}>
                            <ListItemText
                              primary={item.slotLabel}
                              secondary={
                                item.position ? `${item.playerName} (${item.position})` : item.playerName
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid size={{ xs: 12, md: 6 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" className="mb-2">
                      Away lineup
                    </Typography>
                    <Typography variant="body2" color="text.secondary" className="mb-2">
                      {match.away.name} — tactic: {match.away.tactic ?? "-"}
                    </Typography>
                    {awayLineup.length === 0 ? (
                      <Typography variant="body2" color="text.secondary">
                        Нет данных о составе.
                      </Typography>
                    ) : (
                      <List dense>
                        {awayLineup.map((item) => (
                          <ListItem key={`${item.slot}-${item.playerName}`}>
                            <ListItemText
                              primary={item.slotLabel}
                              secondary={
                                item.position ? `${item.playerName} (${item.position})` : item.playerName
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Card>
              <CardContent>
                <Typography variant="h6" className="mb-2">
                  Events
                </Typography>
                {eventsError && <Alert severity="error">{eventsError}</Alert>}
                {eventsLoading ? (
                  <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", p: 4 }}>
                    <CircularProgress size={24} />
                  </Box>
                ) : events.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No events recorded.
                  </Typography>
                ) : (
                  <Stack spacing={1.5}>
                    {events.map((event) => (
                      <Box
                        key={event.id}
                        sx={{
                          border: 1,
                          borderColor: "divider",
                          borderRadius: 2,
                          p: 2,
                        }}
                      >
                        <Typography variant="subtitle2">
                          {event.minute}'
                          {event.type_label ? ` - ${event.type_label}` : ""}
                        </Typography>
                        {event.description && (
                          <Typography variant="body2" color="text.secondary">
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
                )}
              </CardContent>
            </Card>
          </>
        ) : (
          <Alert severity="warning">Match not found.</Alert>
        )}
      </Stack>
    </Box>
  );
}
