import { useCallback, useEffect, useRef, useState } from "react";
import {
  Box,
  Button,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  Stack,
  Switch,
  Typography,
} from "@mui/material";

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
          control={<Switch size="small" checked={autoPlay} onChange={(e) => setAutoPlay(e.target.checked)} />}
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
            possession_seconds: summary?.possession_seconds,
            possession_swings: summary?.possession_swings,
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
