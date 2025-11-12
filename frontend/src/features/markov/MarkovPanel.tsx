import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  Alert,
  Box,
  Button,
  ButtonGroup,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";
import { alpha, useTheme } from "@mui/material/styles";
import AutorenewIcon from "@mui/icons-material/Autorenew";
import SportsSoccerIcon from "@mui/icons-material/SportsSoccer";
import GavelIcon from "@mui/icons-material/Gavel";
import FlagCircleIcon from "@mui/icons-material/FlagCircle";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import WhatshotIcon from "@mui/icons-material/Whatshot";
import MilitaryTechIcon from "@mui/icons-material/MilitaryTech";

export type MarkovPanelMode = "manual" | "live";

interface MarkovPanelProps {
  matchId: number;
  homeName: string;
  awayName: string;
  onMinute?: (summary: any) => void;
  liveSummary?: any;
  mode?: MarkovPanelMode;
}

export function MarkovPanel({
  matchId,
  homeName,
  awayName,
  onMinute,
  liveSummary,
  mode = "live",
}: MarkovPanelProps) {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoPlay, setAutoPlay] = useState(true);
  const [speed, setSpeed] = useState<1 | 2 | 4>(1);
  const [regMinutes, setRegMinutes] = useState<number>(90);
  const tokenRef = useRef<any>(null);
  const autoTimeoutRef = useRef<number | null>(null);
  const autoPlayRef = useRef(autoPlay);
  const lastFetchAtRef = useRef<number | null>(null);
  const theme = useTheme();
  const liveMode = mode === "live" || typeof liveSummary !== "undefined";

  const SPEED_INTERVALS: Record<1 | 2 | 4, number> = {
    1: 60000,
    2: 30000,
    4: 15000,
  };
  const intervalMs = SPEED_INTERVALS[speed];
  const API_BASE = (import.meta as any)?.env?.VITE_API_BASE || "http://127.0.0.1:8000";

  const clearAutoTimeout = useCallback(() => {
    if (autoTimeoutRef.current !== null) {
      window.clearTimeout(autoTimeoutRef.current);
      autoTimeoutRef.current = null;
    }
  }, []);

  const fetchMinute = useCallback(async () => {
    if (liveMode) {
      return;
    }
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

      const minuteSummary = {
        ...data.minute_summary,
        tick_seconds:
          (data.minute_summary && data.minute_summary.tick_seconds) ??
          data.tick_seconds ??
          10,
      };
      setRegMinutes(Number(data.regulation_minutes ?? 90));
      setSummary(minuteSummary);
      onMinute?.(minuteSummary);
      tokenRef.current = minuteSummary?.token ?? null;
      lastFetchAtRef.current = Date.now();
      if (!autoPlayRef.current) {
        clearAutoTimeout();
      }
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }, [API_BASE, clearAutoTimeout, matchId, homeName, awayName, onMinute, liveMode]);

  const scheduleAutoFetch = useCallback(() => {
    if (liveMode || !autoPlayRef.current) return;
    const currentMinute =
      typeof summary?.minute === "number" ? summary.minute : 0;
    if (currentMinute >= regMinutes) {
      return;
    }
    const elapsed = lastFetchAtRef.current ? Date.now() - lastFetchAtRef.current : 0;
    const delay = Math.max(0, intervalMs - elapsed);
    clearAutoTimeout();
    if (delay === 0) {
      void fetchMinute();
      return;
    }
    autoTimeoutRef.current = window.setTimeout(() => {
      autoTimeoutRef.current = null;
      if (!autoPlayRef.current) return;
      void fetchMinute();
    }, delay);
  }, [clearAutoTimeout, fetchMinute, intervalMs, regMinutes, summary?.minute, liveMode]);
  useEffect(() => {
    if (liveMode) {
      clearAutoTimeout();
      return;
    }
    clearAutoTimeout();
    tokenRef.current = null;
    lastFetchAtRef.current = null;
    onMinute?.(null);
    void fetchMinute();
  }, [clearAutoTimeout, fetchMinute, liveMode, matchId, onMinute]);

  useEffect(
    () => () => {
      onMinute?.(null);
    },
    [onMinute],
  );

  useEffect(() => {
    autoPlayRef.current = autoPlay;
    if (!autoPlay) {
      if (autoTimeoutRef.current !== null) {
        window.clearTimeout(autoTimeoutRef.current);
        autoTimeoutRef.current = null;
      }
    }
  }, [autoPlay]);

  useEffect(() => {
    if (liveMode) {
      clearAutoTimeout();
      return;
    }
    if (!autoPlay || !summary) {
      return;
    }
    scheduleAutoFetch();
    return () => clearAutoTimeout();
  }, [autoPlay, clearAutoTimeout, scheduleAutoFetch, summary, liveMode]);

  useEffect(
    () => () => {
      clearAutoTimeout();
    },
    [clearAutoTimeout],
  );

  useEffect(() => {
    if (!liveMode) return;
    setLoading(false);
    setError(null);
    clearAutoTimeout();
    setSummary(liveSummary ?? null);
    if (liveSummary) {
      tokenRef.current = liveSummary.token ?? null;
      lastFetchAtRef.current = Date.now();
    }
  }, [liveMode, liveSummary, clearAutoTimeout]);

  const p = summary?.possession_pct ?? { home: undefined, away: undefined };
  const ef = summary?.entries_final_third ?? { home: undefined, away: undefined };
  const seconds = summary?.possession_seconds ?? { home: undefined, away: undefined };
  const swings = typeof summary?.possession_swings === "number" ? summary.possession_swings : null;
  const swingsAlert = swings !== null && swings > 2;
  const possHome = typeof p.home === "number" ? Math.round(p.home) : "-";
  const possAway = typeof p.away === "number" ? Math.round(p.away) : "-";
  const secondsHome = typeof seconds.home === "number" ? `${seconds.home}s` : "-";
  const secondsAway = typeof seconds.away === "number" ? `${seconds.away}s` : "-";
  const entriesHomeValue = typeof ef.home === "number" ? ef.home : 0;
  const entriesAwayValue = typeof ef.away === "number" ? ef.away : 0;
  const entriesHot = entriesHomeValue + entriesAwayValue > 0;
  const entriesLabel = `${entriesHomeValue}–${entriesAwayValue}`;
  const deltaHome = typeof summary?.score?.home === "number" ? summary.score.home : 0;
  const deltaAway = typeof summary?.score?.away === "number" ? summary.score.away : 0;
  const goalDelta = deltaHome !== 0 || deltaAway !== 0;
  const goalTeam =
    deltaHome > 0 ? homeName : deltaAway > 0 ? awayName : null;
  const counts = summary?.counts ?? {};
  const shotsCount = typeof counts.shot === "number" ? counts.shot : 0;
  const foulsCount = typeof counts.foul === "number" ? counts.foul : 0;
  const outsCount = typeof counts.out === "number" ? counts.out : 0;
  const gkCount = typeof counts.gk === "number" ? counts.gk : 0;
  const validation = summary?.validation;
  const secondsStatus = validation?.seconds_total;
  const secondsOk = secondsStatus?.ok !== false;
  const secondsLabel = secondsStatus
    ? `Seconds ${secondsStatus.actual ?? "-"} / ${secondsStatus.expected ?? "-"}`
    : "Seconds: n/a";
  const pctStatus = validation?.possession_pct;
  const pctOk = pctStatus?.ok !== false;
  const pctLabel = pctStatus
    ? `Pct diff ±${pctStatus.home_diff ?? "-"} / ±${pctStatus.away_diff ?? "-"}`
    : "Pct: n/a";
  const swingsValidationStatus = validation?.swings;
  const swingsValidationOk = swingsValidationStatus?.ok !== false;
  const swingsValidationLabel = swingsValidationStatus
    ? `Swings ${swingsValidationStatus.actual ?? "-"} = ${swingsValidationStatus.expected ?? "-"}`
    : "Swings: n/a";
  const entriesStatus = validation?.entries_final_third;
  const entriesHomeOk = entriesStatus?.home?.ok !== false;
  const entriesAwayOk = entriesStatus?.away?.ok !== false;
  const entriesValidationOk = entriesHomeOk && entriesAwayOk;
  const entriesValidationLabel = entriesStatus
    ? `Entries H ${entriesStatus.home?.actual ?? "-"} / ${entriesStatus.home?.expected ?? "-"} • A ${entriesStatus.away?.actual ?? "-"} / ${entriesStatus.away?.expected ?? "-"}`
    : "Entries: n/a";
  const validationIssues: string[] = [];
  if (!secondsOk) validationIssues.push("Seconds sum deviates from 60.");
  if (!pctOk) validationIssues.push("Possession % mismatch seconds.");
  if (!swingsValidationOk) validationIssues.push("Turnover count mismatch.");
  if (!entriesValidationOk) validationIssues.push("Final-third entries mismatched.");
  const showMinuteStats = true;
  const minuteStatsLabel = `Minute stats: S${shotsCount} / F${foulsCount} / O${outsCount} / GK${gkCount}`;

  const narrativeItems = useMemo(() => {
    const lines = Array.isArray(summary?.narrative) ? (summary?.narrative as string[]) : [];
    return lines.map((line, index) => {
      const normalized = line.toLowerCase();
      let icon: ReactNode | null = null;
      let backgroundColor: string | undefined;
      let borderColor: string | undefined;
      let textColor: string | undefined;

      const paint = (color: string) => {
        borderColor = color;
        backgroundColor = alpha(color, 0.08);
      };

      if (normalized.includes("turnover")) {
        icon = <AutorenewIcon fontSize="small" sx={{ color: theme.palette.warning.main }} />;
        paint(theme.palette.warning.main);
      } else if (normalized.includes("shot")) {
        icon = <SportsSoccerIcon fontSize="small" sx={{ color: theme.palette.error.main }} />;
        paint(theme.palette.error.main);
      } else if (normalized.includes("foul")) {
        icon = <GavelIcon fontSize="small" sx={{ color: theme.palette.secondary.main }} />;
        paint(theme.palette.secondary.main);
      } else if (normalized.includes("out")) {
        icon = <FlagCircleIcon fontSize="small" sx={{ color: theme.palette.info.main }} />;
        paint(theme.palette.info.main);
      } else if (normalized.includes("kickoff")) {
        icon = <InfoOutlinedIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />;
        backgroundColor = theme.palette.action.hover;
        borderColor = undefined;
        textColor = "text.secondary";
      }

      return {
        line,
        icon,
        backgroundColor,
        borderColor,
        textColor,
        key: `narrative-${index}`,
      };
    });
  }, [summary?.narrative, theme]);

  return (
    <Box sx={{ border: 1, borderColor: "divider", borderRadius: 2, p: 2, mt: 2 }}>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} alignItems="center">
        <Typography variant="subtitle1">Markov v0 (1-minute stream)</Typography>

        {!liveMode && (
          <>
            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                clearAutoTimeout();
                void fetchMinute();
              }}
              disabled={loading || !Number.isFinite(matchId)}
            >
              {loading ? "Loading..." : "Next minute"}
            </Button>

            <ButtonGroup
              size="small"
              variant="outlined"
              color="primary"
              sx={{ ml: 1 }}
            >
              {[1, 2, 4].map((option) => (
                <Button
                  key={option}
                  variant={speed === option ? "contained" : "outlined"}
                  onClick={() => setSpeed(option as 1 | 2 | 4)}
                >
                  {`${option}×`}
                </Button>
              ))}
            </ButtonGroup>

            <Button
              size="small"
              variant={autoPlay ? "outlined" : "contained"}
              color={autoPlay ? "warning" : "success"}
              startIcon={autoPlay ? <PauseIcon /> : <PlayArrowIcon />}
              onClick={() => {
                setAutoPlay((prev) => {
                  const next = !prev;
                  if (next) {
                    if (!summary && !loading) {
                      void fetchMinute();
                    } else {
                      scheduleAutoFetch();
                    }
                  } else {
                    clearAutoTimeout();
                  }
                  return next;
                });
              }}
            >
              {autoPlay ? "Pause" : "Play"}
            </Button>
          </>
        )}

        <Typography
          variant="caption"
          color={autoPlay ? "success.main" : "text.secondary"}
          sx={{ ml: 1 }}
        >
          {liveMode ? "Live feed" : autoPlay ? `Auto running ×${speed}` : "Paused"}
        </Typography>

        <Typography variant="caption" color={error ? "error" : "text.secondary"}>
          {error
            ? `Error: ${error}`
            : loading
            ? "Fetching data..."
            : `Minute: ${summary?.minute ?? 0} / ${regMinutes}`}
        </Typography>
      </Stack>

      {summary ? (
        <>
          <Stack
            direction={{ xs: "column", sm: "row" }}
            spacing={1}
            sx={{ mt: 2, flexWrap: "wrap" }}
            useFlexGap
          >
            <Chip size="small" variant="outlined" label={`Minute: ${summary.minute ?? "-"}`} />
            <Chip
              size="small"
              variant="outlined"
              label={`Poss %: ${possHome} | ${possAway}`}
            />
            <Chip
              size="small"
              variant="outlined"
              label={`Seconds: ${secondsHome}-${secondsAway}`}
            />
            <Chip
              size="small"
              variant={swingsAlert ? "filled" : "outlined"}
              color={swingsAlert ? "warning" : "default"}
              label={`Swings: ${swings ?? "-"}`}
            />
            <Chip
              size="small"
              variant={entriesHot ? "filled" : "outlined"}
              color={entriesHot ? "secondary" : "default"}
              icon={entriesHot ? <WhatshotIcon fontSize="small" /> : undefined}
              label={`Final 3rd: ${entriesLabel}`}
            />
            <Chip
              size="small"
              variant={goalDelta ? "filled" : "outlined"}
              color={goalDelta ? "success" : "default"}
              label={`Δscore: ${deltaHome}:${deltaAway}`}
            />
            <Chip
              size="small"
              variant="outlined"
              label={`End: ${summary?.end_state ?? "-"} (ball: ${summary?.possession_end ?? "-"})`}
            />
          </Stack>
          {(showMinuteStats || goalTeam) && (
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={1}
              sx={{ mt: 1, flexWrap: "wrap" }}
              useFlexGap
            >
              {showMinuteStats && (
                <Chip
                  size="small"
                  variant="outlined"
                  icon={<MilitaryTechIcon fontSize="small" />}
                  label={minuteStatsLabel}
                />
              )}
              {goalTeam && (
                <Chip
                  size="small"
                  color="success"
                  variant="filled"
                  icon={<SportsSoccerIcon fontSize="small" />}
                  label={`GOAL! ${goalTeam}`}
                />
              )}
            </Stack>
          )}
          {(summary.minute === Math.floor(regMinutes / 2) || summary.minute === Math.floor(regMinutes / 2) + 1) && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Half-time reached.
            </Alert>
          )}
          {summary.minute >= regMinutes && summary.minute < regMinutes + 5 && (
            <Alert severity="success" sx={{ mt: summary.minute === regMinutes ? 2 : 1 }}>
              Full-time reached ({summary.minute}')
            </Alert>
          )}
          {validation && (
            <>
              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={1}
                sx={{ mt: 1, flexWrap: "wrap" }}
                useFlexGap
              >
                <Chip
                  size="small"
                  variant={secondsOk ? "outlined" : "filled"}
                  color={secondsOk ? "success" : "error"}
                  label={secondsLabel}
                />
                <Chip
                  size="small"
                  variant={pctOk ? "outlined" : "filled"}
                  color={pctOk ? "success" : "error"}
                  label={pctLabel}
                />
                <Chip
                  size="small"
                  variant={swingsValidationOk ? "outlined" : "filled"}
                  color={swingsValidationOk ? "success" : "error"}
                  label={swingsValidationLabel}
                />
                <Chip
                  size="small"
                  variant={entriesValidationOk ? "outlined" : "filled"}
                  color={entriesValidationOk ? "success" : "error"}
                  label={entriesValidationLabel}
                />
              </Stack>
              {validationIssues.length > 0 && (
                <Alert severity="warning" sx={{ mt: 1 }}>
                  Data checks: {validationIssues.join(" ")}
                </Alert>
              )}
            </>
          )}
        </>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Live data will appear here once the simulation publishes the first minute.
        </Typography>
      )}

      
      {/* Server narrative block removed (duplicate of Events) */}

    </Box>
  );
}

