import { useMemo, type ReactNode } from "react";

import { Link as RouterLink } from "react-router-dom";
import { Alert, Box, Button, Card, CardContent, Chip, CircularProgress, Stack, Typography } from "@mui/material";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import SportsSoccerIcon from "@mui/icons-material/SportsSoccer";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { ChampionshipMatchesList } from "@/features/tournaments/components/ChampionshipMatchesList";
import { ChampionshipStandingsTable } from "@/features/tournaments/components/ChampionshipStandingsTable";
import { useMyChampionship } from "@/hooks/tournaments/useMyChampionship";
import type { ChampionshipStanding } from "@/types/tournaments";

export default function MyChampionshipPage() {
  const { data, loading, error } = useMyChampionship();
  const schedule = useMemo(() => {
    if (!data) return [];
    const base =
      Array.isArray(data.schedule) && data.schedule.length > 0
        ? data.schedule
        : [...(data.last_results ?? []), ...(data.next_matches ?? [])];
    return base
      .slice()
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [data]);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!data) {
    return <Alert severity="info">No active championship found for your club.</Alert>;
  }

  const nextMatch =
    schedule.find((match) => new Date(match.date).getTime() >= Date.now()) ?? (schedule.length > 0 ? schedule[0] : null);
  const nextMatchLabel = nextMatch ? `${nextMatch.home_team.name} vs ${nextMatch.away_team.name}` : "No fixtures";
  const nextMatchDate = nextMatch ? new Date(nextMatch.date).toLocaleString() : "TBD";
  const playedCount = Array.isArray(data.last_results) ? data.last_results.length : 0;
  const upcomingCount = Array.isArray(data.next_matches) ? data.next_matches.length : 0;

  const gapMetric = buildGapToTarget({
    standings: data.standings,
    clubPosition: data.club_position,
    leagueLevel: data.championship.league.level,
  });

  const hero = (
    <HeroBar
      title={data.championship.name}
      subtitle={`${data.championship.league.name} · ${data.championship.season.name} progress`}
      tone="purple"
      kpis={[
        { label: "Position", value: data.club_position ?? "-", icon: <LeaderboardIcon fontSize="small" />, hint: "Current standing" },
        {
          label: "Gap to target",
          value: gapMetric?.value ?? "No data",
          icon: <TrendingUpIcon fontSize="small" />,
          hint: gapMetric?.hint,
          badge: gapMetric?.badge,
          tooltip: gapMetric?.tooltip,
        },
        { label: "Next game", value: nextMatchDate, icon: <EventAvailableIcon fontSize="small" />, hint: nextMatchLabel },
        { label: "Fixtures", value: schedule.length, icon: <SportsSoccerIcon fontSize="small" />, hint: "Season schedule" },
      ]}
      actions={
        <Button component={RouterLink} to={`/championships/${data.championship.id}`} size="small" variant="outlined">
          View details
        </Button>
      }
    />
  );



  const topSection = (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="subtitle1" fontWeight={600}>
            Match focus
          </Typography>
          <Stack direction={{ xs: "column", md: "row" }} spacing={1.5} flexWrap="wrap">
            <Chip label={`Played: ${playedCount}`} />
            <Chip label={`Upcoming: ${upcomingCount}`} />
            <Chip label={`Schedule size: ${schedule.length}`} />
            <Chip label={`Next: ${nextMatchLabel}`} color="secondary" />
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );

  const mainContent = (
    <Card sx={{ minWidth: 0 }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Standings
        </Typography>
        <ChampionshipStandingsTable standings={data.standings} />
      </CardContent>
    </Card>
  );

  const asideContent = (
    <Card sx={{ minWidth: 0 }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2, textAlign: { md: "right" } }}>
          Season schedule
        </Typography>
        {schedule.length === 0 ? (
          <Typography variant="body2">No fixtures available.</Typography>
        ) : (
          <ChampionshipMatchesList matches={schedule} />
        )}
      </CardContent>
    </Card>
  );
  return <PageShell hero={hero} top={topSection} main={mainContent} aside={asideContent} />;
}

type GapMetric = {
  value: string;
  hint: ReactNode;
  badge: {
    label: string;
    tone: "success" | "warning" | "danger";
  };
  tooltip: string;
};

function buildGapToTarget({
  standings,
  clubPosition,
  leagueLevel,
}: {
  standings: ChampionshipStanding[];
  clubPosition?: number | null;
  leagueLevel: number;
}): GapMetric | null {
  if (!Array.isArray(standings) || standings.length === 0 || clubPosition == null) {
    return null;
  }

  const clubRow = standings.find((row) => row.position === clubPosition);
  if (!clubRow) {
    return null;
  }

  const totalTeams = standings.length;
  const relegatedRows = standings.filter((row) => row.is_relegation_zone);
  const firstRelegatedPos =
    relegatedRows.length > 0 ? Math.min(...relegatedRows.map((row) => row.position)) : totalTeams + 1;
  const lastSafePos = Math.min(totalTeams, Math.max(1, firstRelegatedPos - 1));
  const isBottomContext = clubRow.position >= lastSafePos;

  let targetRow: ChampionshipStanding | undefined;
  let targetCategory = "";

  if (clubRow.position <= 3) {
    const leaderRow = standings.find((row) => row.position === 1);
    const runnerUpRow = standings.find((row) => row.position === Math.min(2, totalTeams));
    const chasingLeader = clubRow.position !== 1;
    targetRow = chasingLeader ? leaderRow : runnerUpRow ?? leaderRow;
    targetCategory = chasingLeader ? "Leader" : "Runner-up";
  } else if (isBottomContext) {
    const firstRelegatedRow = standings.find((row) => row.position === firstRelegatedPos);
    const lastSafeRow = standings.find((row) => row.position === lastSafePos);
    targetRow = clubRow.position >= firstRelegatedPos ? lastSafeRow ?? firstRelegatedRow : firstRelegatedRow ?? lastSafeRow;
    targetCategory = "Safety";
  } else {
    const playoffCutoff = Math.min(leagueLevel === 1 ? 4 : 6, totalTeams);
    const cutoffRow = standings.find((row) => row.position === playoffCutoff);
    const outsideRow = standings.find((row) => row.position === Math.min(playoffCutoff + 1, totalTeams));
    targetRow = clubRow.position <= playoffCutoff ? outsideRow ?? cutoffRow : cutoffRow ?? outsideRow;
    targetCategory = `Top-${playoffCutoff}`;
  }

  if (!targetRow || !targetCategory) {
    return null;
  }

  const rawGap = targetRow.points - clubRow.points;
  const neededGap = Math.max(0, rawGap);
  const absGap = Math.abs(rawGap);
  const badge =
    neededGap <= 2
      ? { label: "Close", tone: "success" as const }
      : neededGap <= 5
      ? { label: "Chase", tone: "warning" as const }
      : { label: "Tough", tone: "danger" as const };

  const value =
    rawGap === 0
      ? `Level with ${targetCategory}`
      : rawGap > 0
      ? `${absGap} pts off ${targetCategory}`
      : `${absGap} pts clear ${targetCategory}`;

  const hint = (
    <span>
      You: {clubRow.points} pts (MP {clubRow.matches_played})
    </span>
  );

  return {
    value,
    hint,
    badge,
    tooltip: `Target = ${targetCategory} (auto). Click to change target.`,
  };
}

function formatOrdinal(position: number): string {
  const suffixes: Record<number, string> = { 1: "st", 2: "nd", 3: "rd" };
  const remainder = position % 100;
  if (remainder >= 11 && remainder <= 13) {
    return `${position}th`;
  }
  return `${position}${suffixes[position % 10] ?? "th"}`;
}
