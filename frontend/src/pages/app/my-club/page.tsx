import { useEffect, useMemo, useState } from "react";

import { Alert, Button, Grid, Stack, Typography } from "@mui/material";
import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";

import { ClubActions, ClubBanner } from "./sections";
import { Link as RouterLink } from "react-router-dom";
import { formatLeagueDisplay } from "@/constants/countries";

type ClubSummary = {
  id: number;
  name: string;
  country: string;
  league: string;
  status: string;
  tokens: number;
  money: number;
};

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text.slice(0, 140)}`);
  }
  return (await res.json()) as T;
}

export default function MyClubPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [club, setClub] = useState<ClubSummary | null>(null);

  const formatMetric = (value?: number) => {
    if (typeof value !== "number" || Number.isNaN(value)) return "—";
    try {
      return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
    } catch {
      return String(value);
    }
  };

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setError(null);
        setLoading(true);

        const my = await getJSON<{ id: number }>("/api/my/club/");
        const summary = await getJSON<ClubSummary>(`/api/clubs/${my.id}/summary/`);

        if (!cancelled) {
          setClub(summary);
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load club data");
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  const heroActions = (
    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
      <Button component={RouterLink} to="/my-club/players" size="small" variant="outlined">
        Squad
      </Button>
      <Button component={RouterLink} to="/transfers" size="small" variant="contained">
        Transfers
      </Button>
    </Stack>
  );

  const leagueLabel = useMemo(() => formatLeagueDisplay(club?.country, club?.league), [club]);

  const hero = (
    <HeroBar
      title={club?.name ?? "My Club"}
      subtitle="Your central hub for club metrics and activity"
      tone="green"
      kpis={[
        { label: "Tokens", value: formatMetric(club?.tokens) },
        { label: "Funds", value: formatMetric(club?.money) },
        { label: "Status", value: club?.status ?? "—" },
        { label: "League", value: leagueLabel },
      ]}
      actions={heroActions}
    />
  );

  const alertSection = error ? <Alert severity="error">{error}</Alert> : undefined;

  const mainContent = (
    <Stack spacing={3}>
      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12 }}>
          <ClubBanner club={club} loading={loading} />
        </Grid>
      </Grid>
    </Stack>
  );

  const asideContent = (
    <Stack spacing={3}>
      <ClubActions club={club} loading={loading} />
    </Stack>
  );

  const header = (
    <Stack spacing={0.5}>
      <Typography variant="body2" color="text.secondary">
        {club ? formatLeagueDisplay(club.country, club.league) : "Welcome back!"}
      </Typography>
    </Stack>
  );

  // TODO: Wire upcoming fixtures, activity feed, and finance trends once the corresponding APIs are available.
  return (
    <PageShell
      hero={hero}
      header={header}
      top={alertSection}
      main={mainContent}
      aside={asideContent}
      bottomSplit="67-33"
    />
  );
}
