import { useEffect, useMemo, useState } from "react";

import { Alert, Button, Card, CardContent, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

import ClubPlayersTable from "@/components/club/ClubPlayersTable";
import HeroBar from "@/components/ui/HeroBar";
import PageShell from "@/components/ui/PageShell";

type ClubSummary = {
  id: number;
  name: string;
};

type PlayerSummary = {
  id: number;
  position?: string | null;
  player_class?: number | null;
  overall_rating?: number | null;
  on_loan?: boolean;
  attributes?: { attack?: number; defense?: number };
  last_trained_at?: string | null;
};

type ClubMetrics = {
  rosterSize: number;
  avgOverall: string;
  onLoan: number;
  foreignCount: number;
  lastTraining: string | null;
};

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text.slice(0, 140)}`);
  }
  return (await res.json()) as T;
}

export default function PlayersPage() {
  const [club, setClub] = useState<ClubSummary | null>(null);
  const [metrics, setMetrics] = useState<ClubMetrics>({
    rosterSize: 0,
    avgOverall: "-",
    onLoan: 0,
    foreignCount: 0,
    lastTraining: null,
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setError(null);
        setLoading(true);

        const me = await getJSON<{ id: number }>("/api/my/club/");
        const clubData = await getJSON<ClubSummary>(`/api/clubs/${me.id}/summary/`);
        const players = await getJSON<PlayerSummary[]>(`/clubs/detail/${me.id}/get-players/`);

        if (cancelled) return;

        setClub(clubData);

        const rosterSize = players.length;
        const calcOverall = (p: PlayerSummary) => {
          if (typeof p.overall_rating === "number" && Number.isFinite(p.overall_rating)) return p.overall_rating;
          const atk = p.attributes?.attack ?? null;
          const def = p.attributes?.defense ?? null;
          if (Number.isFinite(atk) && Number.isFinite(def)) return (Number(atk) + Number(def)) / 2;
          if (Number.isFinite(atk)) return Number(atk);
          if (Number.isFinite(def)) return Number(def);
          return null;
        };
        const ratings = players
          .map((p) => calcOverall(p))
          .filter((v): v is number => v !== null && Number.isFinite(v));
        const avgOverallValue =
          ratings.length === 0 ? "-" : (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(1);
        const onLoan = players.filter((p) => Boolean(p.on_loan)).length;
        const lastTrainingIso = (() => {
          const dates = players
            .map((p) => p.last_trained_at)
            .filter((d): d is string => Boolean(d))
            .map((d) => new Date(d))
            .filter((d) => Number.isFinite(d.getTime()));
          if (dates.length === 0) return null;
          const maxDate = new Date(Math.max(...dates.map((d) => d.getTime())));
          return maxDate.toISOString();
        })();

        setMetrics({
          rosterSize,
          avgOverall: avgOverallValue,
          onLoan,
          foreignCount: 0, // no country info available here
          lastTraining: lastTrainingIso,
        });
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load squad data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const heroKpis = useMemo(
    () => [
      { label: "Roster size", value: metrics.rosterSize ? String(metrics.rosterSize) : loading ? "…" : "-" },
      { label: "Average OVR", value: loading ? "…" : metrics.avgOverall },
      { label: "Players on loan", value: loading ? "…" : String(metrics.onLoan) },
      { label: "Foreign quota", value: loading ? "…" : String(metrics.foreignCount) },
      {
        label: "Last training",
        value:
          loading || !metrics.lastTraining
            ? loading
              ? "…"
              : "-"
            : new Date(metrics.lastTraining).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      },
    ],
    [metrics, loading]
  );

  const hero = (
    <HeroBar
      title="Squad"
      subtitle="Manage your roster composition and depth chart"
      tone="green"
      kpis={heroKpis}
      actions={
        <Button component={RouterLink} to="/transfers" size="small" variant="outlined">
          Go to transfers
        </Button>
      }
    />
  );

  const top = (
    <>
      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}
      <Typography variant="body2" color="text.secondary">
        Use filters in the table to manage positions, contracts and depth. Click a player name to open the detailed profile.
      </Typography>
    </>
  );

  const mainContent = (
    <Card>
      <CardContent sx={{ p: 0 }}>
        <ClubPlayersTable />
      </CardContent>
    </Card>
  );

  const asideContent = (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Squad tips
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Keep at least two players per position and track fatigue before each matchday. Use the transfers page to offload surplus players
          or sign short-term replacements.
        </Typography>
      </CardContent>
    </Card>
  );

  return <PageShell hero={hero} top={top} main={mainContent} aside={asideContent} bottomSplit="67-33" />;
}
