import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link as RouterLink, useParams } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  FormControlLabel,
  Grid,
  IconButton,
  Link,
  List,
  ListItem,
  ListItemText,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

import {
  fetchMatchDetail,
  fetchMatchEvents,
  MatchDetail,
  MatchEvent,
  MatchStatus,
  simulateMatch,
  substitutePlayer,
} from "@/api/matches";

const TIME_FORMATTER = new Intl.DateTimeFormat(undefined, {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
});

const AUTO_REFRESH_MS = 15000;

const WS_BASE_URL =
  typeof import.meta.env.VITE_WS_BASE_URL === "string"
    ? import.meta.env.VITE_WS_BASE_URL.replace(/\/$/, "")
    : undefined;

const STATUS_LABELS: Record<MatchStatus, string> = {
  scheduled: "Scheduled",
  in_progress: "In Progress",
  paused: "Paused",
  finished: "Finished",
  cancelled: "Cancelled",
  error: "Error",
};

const fallbackStatusLabel = (status?: string, previous?: string) => {
  if (!status) return previous ?? "";
  const mapped = STATUS_LABELS[status as MatchStatus];
  if (mapped) return mapped;
  const parts = status.split("_").map((part) => part.charAt(0).toUpperCase() + part.slice(1));
  return parts.join(" ");
};

const generateEventId = () => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `ws-${Date.now()}-${Math.random().toString(36).slice(2)}`;
};

function MarkovPanel({ matchId, homeName, awayName }: { matchId: number; homeName: string; awayName: string; }) {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoPlay, setAutoPlay] = useState(true);
  const [regMinutes, setRegMinutes] = useState<number>(90);
  const tokenRef = useRef<any>(null);

  const PLAY_INTERVAL_MS = 2000;
  const API_BASE = (import.meta as any)?.env?.VITE_API_BASE || "http://127.0.0.1:8000";

  const fetchMinute = useCallback(async () => {
    if (!Number.isFinite(matchId) || matchId <= 0) return;
    setLoading(true);
    setError(null);
    try {
      const url = new URL(`${API_BASE}/matches/markov-minute/`);
      url.searchParams.set("home", homeName);
      url.searchParams.set("away", awayName);
      url.searchParams.set("seed", String(matchId));
      if (tokenRef.current) {
        url.searchParams.set("token", JSON.stringify(tokenRef.current));
      }
      const response = await fetch(url.toString(), { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      setRegMinutes(Number(data.regulation_minutes ?? 90));
      setSummary(data.minute_summary);
      tokenRef.current = data.minute_summary?.token ?? null;
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }, [API_BASE, matchId]);

  useEffect(() => {
    tokenRef.current = null;
    void fetchMinute();
  }, [fetchMinute, matchId]);

  useEffect(() => {
    if (!autoPlay) return;
    if (!Number.isFinite(matchId) || matchId <= 0) return;

    const id = window.setInterval(() => {
      const currentMinute = Number(summary?.minute ?? 0);
      if (currentMinute >= regMinutes) {
        setAutoPlay(false);
        return;
      }
      if (!loading) {
        void fetchMinute();
      }
    }, PLAY_INTERVAL_MS);

    return () => window.clearInterval(id);
  }, [autoPlay, fetchMinute, loading, matchId, regMinutes, summary?.minute]);

  const p = summary?.possession_pct ?? { home: 0, away: 0 };
  const ef = summary?.entries_final_third ?? { home: 0, away: 0 };

  return (
    <Box sx={{ border: 1, borderColor: "divider", borderRadius: 2, p: 2, mt: 2 }}>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} alignItems="center">
        <Typography variant="subtitle1">Markov v0 (1-minute stream)</Typography>

        <Button
          variant="outlined"
          size="small"
          onClick={() => fetchMinute()}
          disabled={loading || !Number.isFinite(matchId)}
        >
          {loading ? "Loading..." : "Next minute"}
        </Button>

        <FormControlLabel
          sx={{ ml: 1 }}
          control={
            <Switch size="small" checked={autoPlay} onChange={(e) => setAutoPlay(e.target.checked)} />
          }
          label="Auto"
        />

        <Typography variant="caption" color={error ? "error" : "text.secondary"}>
          {error
            ? `Error: ${error}`
            : loading
            ? "Fetching data..."
            : `Minute: ${summary?.minute ?? 0} / ${regMinutes}`}
        </Typography>
      </Stack>

      <Box component="pre" sx={{ mt: 2, backgroundColor: "grey.100", p: 2, borderRadius: 1, fontSize: 12, overflowX: "auto" }}>
        {JSON.stringify(
          {
            minute: summary?.minute,
            start_state: summary?.start_state,
            end_state: summary?.end_state,
            possession_end: summary?.possession_end,
            possession_pct: p,
            entries_final_third: ef,
            score_delta: summary?.score,
            score_total: summary?.score_total,
          },
          null,
          2
        )}
      </Box>

      <Box component="pre" sx={{ mt: 2, backgroundColor: "grey.100", p: 2, borderRadius: 1, fontSize: 12, height: 180, overflow: "auto" }}>
        {JSON.stringify(summary?.events ?? [], null, 2)}
      </Box>
      <Typography variant="subtitle2" sx={{ mt: 2 }}>
        Narrative (server)
      </Typography>
      <List dense>
        {(summary?.narrative ?? []).map((line: string, i: number) => (
          <ListItem key={i} disableGutters sx={{ py: 0.25 }}>
            <ListItemText primary={line} />
          </ListItem>
        ))}
      </List>

    </Box>
  );
}

function formatTimestamp(value: string | null) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return TIME_FORMATTER.format(date);
}

export default function MatchLivePage() {
  const { matchId: matchIdParam } = useParams<{ matchId: string }>();
  const matchId = Number(matchIdParam);

  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [events, setEvents] = useState<MatchEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [simulateLoading, setSimulateLoading] = useState(false);
  const [substituting, setSubstituting] = useState(false);
  const [outPlayerId, setOutPlayerId] = useState("");
  const [inPlayerId, setInPlayerId] = useState("");
  const [subDescription, setSubDescription] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const autoRefreshManualRef = useRef(false);
  const wsAdjustedAutoRef = useRef(false);
  const wsSupported = useMemo(() => typeof window !== "undefined" && "WebSocket" in window, []);

  const mapWebSocketEvent = useCallback((event: any): MatchEvent => {
    const minuteValue = Number(event?.minute);
    return {
      id: event?.id ?? generateEventId(),
      minute: Number.isFinite(minuteValue) ? minuteValue : 0,
      type: event?.type ?? event?.event_type ?? "update",
      type_label: event?.type_label ?? event?.event_type ?? "Event",
      description: event?.description ?? "",
      personality_reason: event?.personality_reason ?? null,
      timestamp: event?.timestamp ?? null,
      player: event?.player_name || event?.player?.name
        ? {
            id: event?.player?.id ?? null,
            name: event?.player?.name ?? event?.player_name ?? null,
            position: event?.player?.position ?? null,
          }
        : null,
      related_player: event?.related_player_name || event?.related_player?.name
        ? {
            id: event?.related_player?.id ?? null,
            name: event?.related_player?.name ?? event?.related_player_name ?? null,
            position: event?.related_player?.position ?? null,
          }
        : null,
    };
  }, []);

  const applyMatchUpdate = useCallback(
    (payload: any) => {
      if (!payload) return;

      setMatch((previous) => {
        if (!previous) return previous;

        const next: MatchDetail = {
          ...previous,
          current_minute:
            payload.minute !== undefined && payload.minute !== null
              ? Number(payload.minute)
              : previous.current_minute,
          waiting_for_next_minute:
            payload.waiting_for_next_minute ?? previous.waiting_for_next_minute,
          processed: payload.processed ?? previous.processed,
          score: {
            home:
              payload.home_score !== undefined && payload.home_score !== null
                ? Number(payload.home_score)
                : previous.score.home,
            away:
              payload.away_score !== undefined && payload.away_score !== null
                ? Number(payload.away_score)
                : previous.score.away,
          },
          stats: {
            ...previous.stats,
            shoots:
              payload.st_shoots !== undefined && payload.st_shoots !== null
                ? Number(payload.st_shoots)
                : previous.stats.shoots,
            passes:
              payload.st_passes !== undefined && payload.st_passes !== null
                ? Number(payload.st_passes)
                : previous.stats.passes,
            possessions:
              payload.st_possessions !== undefined && payload.st_possessions !== null
                ? Number(payload.st_possessions)
                : previous.stats.possessions,
            fouls:
              payload.st_fouls !== undefined && payload.st_fouls !== null
                ? Number(payload.st_fouls)
                : previous.stats.fouls,
            injuries:
              typeof payload.st_injury === "number"
                ? payload.st_injury
                : Array.isArray(payload.st_injury)
                ? payload.st_injury.length
                : previous.stats.injuries,
            home_momentum:
              payload.home_momentum !== undefined && payload.home_momentum !== null
                ? Number(payload.home_momentum)
                : previous.stats.home_momentum,
            away_momentum:
              payload.away_momentum !== undefined && payload.away_momentum !== null
                ? Number(payload.away_momentum)
                : previous.stats.away_momentum,
            home_pass_streak: previous.stats.home_pass_streak,
            away_pass_streak: previous.stats.away_pass_streak,
          },
        };

        if (payload.status) {
          next.status = payload.status;
          next.status_label = fallbackStatusLabel(payload.status, previous.status_label);
        }

        if (payload.last_minute_update) {
          next.last_minute_update = payload.last_minute_update;
        }
        if (payload.started_at) {
          next.started_at = payload.started_at;
        }
        if (payload.datetime) {
          next.datetime = payload.datetime;
        }

        return next;
      });

      if (Array.isArray(payload.events)) {
        setEvents((prevEvents) => {
          const mapped = payload.events.map(mapWebSocketEvent);
          const eventKey = (evt: MatchEvent) =>
            `${evt.minute}|${evt.type}|${evt.description}|${evt.player?.name ?? ""}|${
              evt.related_player?.name ?? ""
            }`;

          if (payload.partial_update) {
            const existing = new Set(prevEvents.map(eventKey));
            const unique = mapped.filter((evt) => !existing.has(eventKey(evt)));
            if (unique.length === 0) {
              return prevEvents;
            }
            const mergedEvents = [...prevEvents, ...unique];
            mergedEvents.sort((a, b) => {
              if (a.minute !== b.minute) {
                return a.minute - b.minute;
              }
              return (a.description ?? "").localeCompare(b.description ?? "");
            });
            return mergedEvents;
          }

          return mapped.sort((a, b) => {
            if (a.minute !== b.minute) {
              return a.minute - b.minute;
            }
            return (a.description ?? "").localeCompare(b.description ?? "");
          });
        });
      }
    },
    [mapWebSocketEvent]
  );

  const matchInProgress = match?.status === "in_progress";
  const matchFinished = match?.status === "finished";

  const loadData = useCallback(
    async (showSpinner = false) => {
      if (!Number.isFinite(matchId)) {
        setError("Invalid match id");
        setLoading(false);
        return;
      }

      if (showSpinner) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      try {
        const [detail, eventsResponse] = await Promise.all([fetchMatchDetail(matchId), fetchMatchEvents(matchId)]);
        setMatch(detail);
        setEvents(eventsResponse.events);
        setError(null);
      } catch (e: any) {
        setError(e?.message ?? "Failed to load live data");
      } finally {
        if (showSpinner) {
          setLoading(false);
        }
        setRefreshing(false);
      }
    },
    [matchId],
  );

  useEffect(() => {
    loadData(true);
  }, [loadData]);

  useEffect(() => {
    if (!Number.isFinite(matchId) || !wsSupported || typeof window === "undefined") {
      if (!wsSupported) {
        setWsError("WebSocket not supported. Falling back to polling mode.");
      }
      return;
    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const base = WS_BASE_URL ?? `${protocol}://${window.location.host}`;
    const socketUrl = `${base}/ws/match/${matchId}/`;

    let cancelled = false;
    let socket: WebSocket | null;

    try {
      socket = new WebSocket(socketUrl);
    } catch (err) {
      setWsError("Failed to establish live connection.");
      return;
    }

    wsRef.current = socket;

    socket.onopen = () => {
      if (cancelled) return;
      setWsConnected(true);
      setWsError(null);
      if (!autoRefreshManualRef.current) {
        wsAdjustedAutoRef.current = true;
        setAutoRefresh(false);
      }
    };

    socket.onmessage = (event) => {
      if (cancelled) return;
      try {
        const message = JSON.parse(event.data);
        if (message?.type === "match_update") {
          applyMatchUpdate(message.data);
        } else if (message?.type === "error") {
          setWsError(message.message ?? "Live updates unavailable.");
        }
      } catch (err) {
        console.warn("Failed to parse live match update:", err);
      }
    };

    socket.onerror = () => {
      if (cancelled) return;
      setWsError("WebSocket connection error. Polling will continue.");
    };

    socket.onclose = () => {
      if (cancelled) return;
      setWsConnected(false);
      if (!autoRefreshManualRef.current && wsAdjustedAutoRef.current) {
        setAutoRefresh(true);
      }
      wsAdjustedAutoRef.current = false;
    };

    return () => {
      cancelled = true;
      setWsConnected(false);
      if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
        socket.close();
      }
      wsRef.current = null;
    };
  }, [matchId, applyMatchUpdate, wsSupported]);

  useEffect(() => {
    if (!autoRefresh || !Number.isFinite(matchId)) {
      return undefined;
    }
    const interval = window.setInterval(() => {
      loadData(false);
    }, AUTO_REFRESH_MS);
    return () => window.clearInterval(interval);
  }, [autoRefresh, loadData, matchId]);

  useEffect(() => {
    if (!matchFinished) {
      return;
    }
    if (!autoRefreshManualRef.current) {
      setAutoRefresh(false);
    }
    wsAdjustedAutoRef.current = false;
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
  }, [matchFinished]);

  const handleSimulate = async (mode: "step" | "full") => {
    if (!Number.isFinite(matchId)) return;
    if (!matchInProgress) {
      setActionError("Match is not currently in progress.");
      return;
    }
    try {
      setSimulateLoading(true);
      setActionError(null);
      const response = await simulateMatch(matchId, { mode });
      setMatch(response.match);

      if (response.events.length) {
        setEvents((prev) => {
          const merged = [...prev, ...response.events];
          return merged.sort((a, b) => (a.minute === b.minute ? a.id - b.id : a.minute - b.minute));
        });
      } else {
        const eventsResponse = await fetchMatchEvents(matchId);
        setEvents(eventsResponse.events);
      }

      setActionMessage(mode === "full" ? "Match simulated to the end." : "Simulated one action.");
    } catch (e: any) {
      setActionError(e?.message ?? "Simulation failed");
    } finally {
      setSimulateLoading(false);
    }
  };

  const handleSubstitute = async () => {
    if (!Number.isFinite(matchId)) return;
    if (!matchInProgress) {
      setActionError("Match is not currently in progress.");
      return;
    }
    const outId = Number(outPlayerId);
    if (!Number.isFinite(outId) || outId <= 0) {
      setActionError("Enter a valid outgoing player ID");
      return;
    }

    const inId = Number(inPlayerId);
    const payload = {
      outPlayerId: outId,
      inPlayerId: Number.isFinite(inId) && inId > 0 ? inId : undefined,
      description: subDescription.trim() || undefined,
    };

    try {
      setSubstituting(true);
      setActionError(null);
      const response = await substitutePlayer(matchId, payload);

      setMatch(response.match);
      setEvents((prev) => {
        const merged = [...prev, response.event];
        return merged.sort((a, b) => (a.minute === b.minute ? a.id - b.id : a.minute - b.minute));
      });

      const outName = response.event.player?.name ?? `#${outId}`;
      const inName = response.event.related_player?.name;
      setActionMessage(
        inName ? `${outName} replaced by ${inName}.` : `${outName} substituted.`,
      );

      setOutPlayerId("");
      setInPlayerId("");
      setSubDescription("");
    } catch (e: any) {
      setActionError(e?.message ?? "Substitution failed");
    } finally {
      setSubstituting(false);
    }
  };

  // --------- ИЗМЕНЕНО: группируем события по минутам и рисуем 1 карточку на минуту ----------
  const eventItems = useMemo(() => {
    if (!events.length) {
      return null;
    }

    // Группировка по минутам
    const byMinute = new Map<number, MatchEvent[]>();
    for (const ev of events) {
      const m = Number(ev.minute ?? 0);
      if (!byMinute.has(m)) byMinute.set(m, []);
      byMinute.get(m)!.push(ev);
    }

    // Последняя (текущая) минута сверху, чтобы новые события сразу были видны.
    const minutes = Array.from(byMinute.keys()).sort((a, b) => b - a);

    return minutes.map((minute) => {
      const list = byMinute.get(minute)!;

      return (
        <Box
          key={`minute-${minute}`}
          sx={{
            border: 1,
            borderColor: "divider",
            borderRadius: 2,
            overflow: "hidden",
          }}
        >
          {/* Заголовок карточки минуты */}
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

          {/* События этой минуты */}
          <Stack spacing={1.5} sx={{ p: 2 }}>
            {list.map((event) => (
              <Box key={event.id}>
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  spacing={1}
                  justifyContent="space-between"
                >
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
    });
  }, [events]);
  // --------- КОНЕЦ ИЗМЕНЕНИЙ ---------------------------------------------------

  return (
    <Box sx={{ p: { xs: 2, sm: 4 } }}>
      <Stack spacing={3}>
        <Stack direction="row" spacing={1} alignItems="center">
          <IconButton component={RouterLink} to="/matches" color="primary">
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h1" component="h1" className="mb-0">
            Live Match
          </Typography>
        </Stack>

        {error && <Alert severity="error">{error}</Alert>}
        {actionMessage && (
          <Alert severity="success" onClose={() => setActionMessage(null)}>
            {actionMessage}
          </Alert>
        )}
        {actionError && (
          <Alert severity="warning" onClose={() => setActionError(null)}>
            {actionError}
          </Alert>
        )}
        {wsError && (
          <Alert severity="info" onClose={() => setWsError(null)}>
            {wsError}
          </Alert>
        )}

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
                        Status: {match.status_label} | Minute: {match.current_minute}
                      </Typography>
                    </Stack>
                  </Grid>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Stack spacing={1} alignItems="flex-end">
                      <Typography variant="h2">
                        {match.score.home} : {match.score.away}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Last update: {formatTimestamp(match.last_minute_update)}
                      </Typography>
                    </Stack>
                  </Grid>
                </Grid>

                <Stack
                  direction={{ xs: "column", md: "row" }}
                  justifyContent="space-between"
                  alignItems={{ xs: "flex-start", md: "center" }}
                  spacing={2}
                  sx={{ mt: 2 }}
                >
                  <Stack direction="row" spacing={1}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleSimulate("step")}
                      disabled={simulateLoading || !matchInProgress}
                    >
                      Simulate Action
                    </Button>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => handleSimulate("full")}
                      disabled={simulateLoading || !matchInProgress}
                    >
                      Simulate To End
                    </Button>
                  </Stack>
                  <Stack spacing={1} alignItems={{ xs: "flex-start", sm: "center" }}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Button
                        variant="text"
                        size="small"
                        onClick={() => loadData(false)}
                        disabled={refreshing}
                      >
                        {refreshing ? "Refreshing..." : "Refresh"}
                      </Button>
                      <Button
                        component={RouterLink}
                        to={`/matches/${match.id}`}
                        size="small"
                        variant="text"
                      >
                        Open match details
                      </Button>
                      {matchFinished && (
                        <Button component={RouterLink} to="/matches" size="small" variant="text">
                          Back to matches
                        </Button>
                      )}
                    </Stack>
                    <Typography
                      variant="caption"
                      color={wsConnected ? "success.main" : "text.secondary"}
                    >
                      {wsConnected ? "Live updates connected" : "Polling mode active"}
                    </Typography>
                  </Stack>
                </Stack>

                {matchFinished && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    Match finished. Review the summary or return to the matches list.
                  </Alert>
                )}

                <Divider sx={{ my: 3 }} />

                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Typography variant="subtitle1">Home</Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {match.home.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tactic: {match.home.tactic ?? "-"}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Typography variant="subtitle1">Away</Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {match.away.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tactic: {match.away.tactic ?? "-"}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <MarkovPanel
              matchId={Number(match?.id ?? matchId)}
              homeName={match.home.name}
              awayName={match.away.name}
            />

            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Card>
                  <CardContent>
                    <Stack
                      direction={{ xs: "column", sm: "row" }}
                      justifyContent="space-between"
                      alignItems={{ xs: "flex-start", sm: "center" }}
                      spacing={1.5}
                    >
                      <Typography variant="h6">Live Controls</Typography>
                      <FormControlLabel
                        control={
                          <Switch
                            size="small"
                            checked={autoRefresh}
                            onChange={(event) => {
                              autoRefreshManualRef.current = true;
                              setAutoRefresh(event.target.checked);
                            }}
                          />
                        }
                        label="Auto refresh"
                      />
                    </Stack>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Auto refresh polls every {AUTO_REFRESH_MS / 1000} seconds while the match is in progress.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" className="mb-2">
                      Substitution
                    </Typography>
                    <Stack spacing={2}>
                      <TextField
                        label="Player out (ID)"
                        value={outPlayerId}
                        type="number"
                        onChange={(event) => setOutPlayerId(event.target.value)}
                        size="small"
                      />
                      <TextField
                        label="Player in (ID)"
                        value={inPlayerId}
                        type="number"
                        onChange={(event) => setInPlayerId(event.target.value)}
                        size="small"
                      />
                      <TextField
                        label="Comment (optional)"
                        value={subDescription}
                        onChange={(event) => setSubDescription(event.target.value)}
                        size="small"
                        multiline
                        minRows={2}
                      />
                      <Button
                        variant="contained"
                        onClick={handleSubstitute}
                        disabled={substituting || !matchInProgress}
                      >
                        {substituting ? "Submitting..." : "Apply Substitution"}
                      </Button>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Card>
              <CardContent>
                <Typography variant="h6" className="mb-2">
                  Events
                </Typography>
                {!events.length ? (
                  <Typography variant="body2" color="text.secondary">
                    No events recorded yet.
                  </Typography>
                ) : (
                  <Stack spacing={1.5}>{eventItems}</Stack>
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
