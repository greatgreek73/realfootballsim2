import { useEffect, useMemo, useState } from "react";

import { Alert, Button, Grid, Stack, Typography } from "@mui/material";
import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";

import {
  ClubActions,
  ClubActivity,
  ClubBanner,
  ClubFinancePlaceholder,
  ClubSchedule,
  ClubStats,
} from "./sections";
import type { ClubActivityItem, ClubFixture } from "./sections";
import { Link as RouterLink } from "react-router-dom";
import { fetchMatches, MatchSummary } from "@/api/matches";

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
  const [matchesLoading, setMatchesLoading] = useState(true);
  const [matchesError, setMatchesError] = useState<string | null>(null);
  const [upcomingFixtures, setUpcomingFixtures] = useState<ClubFixture[]>([]);
  const [recentActivity, setRecentActivity] = useState<ClubActivityItem[]>([]);

  const dateFormatter = useMemo(
    () =>
      new Intl.DateTimeFormat(undefined, {
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      }),
    [],
  );

  const formatDate = (value: string | null) => {
    if (!value) return "TBD";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return dateFormatter.format(date);
  };

  const formatMetric = (value?: number) => {
    if (typeof value !== "number" || Number.isNaN(value)) return "—";
    try {
      return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
    } catch {
      return String(value);
    }
  };

  const buildFixture = (match: MatchSummary, clubId: number): ClubFixture => {
    const isHome = match.home.id === clubId;
    const opponent = isHome ? match.away.name : match.home.name;
    return {
      id: match.id,
      opponent: `${isHome ? "vs" : "@"} ${opponent}`,
      date: formatDate(match.datetime),
      venue: isHome ? "Home" : "Away",
    };
  };

  const buildActivityItems = (matches: MatchSummary[], clubId: number): ClubActivityItem[] =>
    matches.map((match) => {
      const isHome = match.home.id === clubId;
      const opponent = isHome ? match.away.name : match.home.name;
      const vsLabel = isHome ? `vs ${opponent}` : `@ ${opponent}`;
      const score = `${match.score.home} : ${match.score.away}`;
      const competition = match.competition?.name ?? "Friendly";
      return {
        id: match.id,
        title: `${match.status_label} - ${score} ${vsLabel}`,
        description: competition,
        time: formatDate(match.datetime),
      };
    });

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
          setMatchesLoading(true);
          setMatchesError(null);
          try {
            const [upcoming, recent] = await Promise.all([
              fetchMatches({ clubId: summary.id, processed: false, ordering: "datetime", pageSize: 5 }),
              fetchMatches({ clubId: summary.id, processed: true, ordering: "-datetime", pageSize: 5 }),
            ]);

            if (!cancelled) {
              setUpcomingFixtures(upcoming.results.map((match) => buildFixture(match, summary.id)));
              setRecentActivity(buildActivityItems(recent.results, summary.id));
            }
          } catch (matchesErr: any) {
            if (!cancelled) setMatchesError(matchesErr?.message ?? "Failed to load matches");
          } finally {
            if (!cancelled) setMatchesLoading(false);
          }
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load club data");
      } finally {
        if (!cancelled) {
          setLoading(false);
          setMatchesLoading(false);
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

  const hero = (
    <HeroBar
      title={club?.name ?? "My Club"}
      subtitle="Your central hub for club metrics and activity"
      tone="green"
      kpis={[
        { label: "Tokens", value: formatMetric(club?.tokens) },
        { label: "Funds", value: formatMetric(club?.money) },
        { label: "Status", value: club?.status ?? "—" },
        { label: "League", value: club?.league ?? "—" },
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

      <Grid container size={12} spacing={2.5}>
        <ClubStats club={club} loading={loading} />
      </Grid>

      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12 }}>
          <ClubSchedule loading={loading || matchesLoading} fixtures={upcomingFixtures} error={matchesError} />
        </Grid>
      </Grid>
    </Stack>
  );

  const asideContent = (
    <Stack spacing={3}>
      <ClubActions club={club} loading={loading} />
      <ClubActivity loading={loading || matchesLoading} items={recentActivity} error={matchesError} />
      <ClubFinancePlaceholder loading={loading} />
    </Stack>
  );

  const header = (
    <Stack spacing={0.5}>
      <Typography variant="body2" color="text.secondary">
        {club ? [club.country, club.league].filter(Boolean).join(" • ") : "Welcome back!"}
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
