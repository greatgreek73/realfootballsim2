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
import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";

export function MarkovPanel({
  matchId,
  homeName,
  awayName,
  onMinute,
}: {
  matchId: number;
  homeName: string;
  awayName: string;
  onMinute?: (summary: any) => void;
}) {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoPlay, setAutoPlay] = useState(true);
  const [speed, setSpeed] = useState<1 | 2 | 4>(1);
  const [regMinutes, setRegMinutes] = useState<number>(90);
  const tokenRef = useRef<any>(null);
  const theme = useTheme();

  const SPEED_INTERVALS: Record<1 | 2 | 4, number> = {
    1: 2000,
    2: 1000,
    4: 500,
  };
  const intervalMs = SPEED_INTERVALS[speed];
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

      const minuteSummary = data.minute_summary;
      setRegMinutes(Number(data.regulation_minutes ?? 90));
      setSummary(minuteSummary);
      onMinute?.(minuteSummary);
      tokenRef.current = minuteSummary?.token ?? null;
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }, [API_BASE, matchId, homeName, awayName, onMinute]);

  useEffect(() => {
    tokenRef.current = null;
    onMinute?.(null);
    void fetchMinute();
  }, [fetchMinute, matchId, onMinute]);

  useEffect(
    () => () => {
      onMinute?.(null);
    },
    [onMinute],
  );

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
    }, intervalMs);

    return () => window.clearInterval(id);
  }, [autoPlay, fetchMinute, intervalMs, loading, matchId, regMinutes, summary?.minute]);

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

        <Button
          variant="outlined"
          size="small"
          onClick={() => fetchMinute()}
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
              {option}×
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
              if (next && !loading) {
                void fetchMinute();
              }
              return next;
            });
          }}
        >
          {autoPlay ? "Pause" : "Play"}
        </Button>

        <Typography
          variant="caption"
          color={autoPlay ? "success.main" : "text.secondary"}
          sx={{ ml: 1 }}
        >
          {autoPlay ? `Auto running… ×${speed}` : "Paused"}
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
            <Chip
              size="small"
              variant="outlined"
              icon={<MilitaryTechIcon fontSize="small" />}
              label={minuteStatsLabel}
            />
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
          {summary.minute >= 45 && summary.minute <= 46 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              Half-time reached.
            </Alert>
          ) : null}
          {summary.minute >= 90 ? (
            <Alert severity="success" sx={{ mt: summary.minute === 90 ? 2 : 1 }}>
              Full-time reached ({summary.minute}')
            </Alert>
          ) : null}
        </>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Нет данных для текущей минуты — нажмите «Next minute».
        </Typography>
      )}

      <Divider sx={{ my: 2 }} />

      <Typography variant="subtitle2" sx={{ mt: 2 }}>
        Narrative (server)
      </Typography>
      <List dense disablePadding>
        {narrativeItems.length === 0 ? (
          <ListItem disableGutters>
            <ListItemText
              primary="Narrative недоступен для этой минуты."
              primaryTypographyProps={{ variant: "body2", color: "text.secondary" }}
            />
          </ListItem>
        ) : (
          narrativeItems.map(({ key, line, icon, backgroundColor, borderColor, textColor }) => (
            <ListItem
              key={key}
              disableGutters
              sx={{
                py: 0.75,
                px: icon ? 1 : 1.5,
                borderRadius: 1,
                alignItems: "flex-start",
                backgroundColor,
                borderLeft: borderColor ? `3px solid ${borderColor}` : undefined,
                "&:not(:last-of-type)": { mb: 0.5 },
              }}
            >
              {icon && (
                <ListItemIcon sx={{ minWidth: 28, mt: 0.2 }}>
                  {icon}
                </ListItemIcon>
              )}
              <ListItemText
                primary={line}
                primaryTypographyProps={{ variant: "body2", color: textColor ?? "text.primary" }}
              />
            </ListItem>
          ))
        )}
      </List>
    </Box>
  );
}
