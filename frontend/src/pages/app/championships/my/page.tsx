import { useMemo, type ReactNode } from "react";

import { Link as RouterLink } from "react-router-dom";
import { Alert, Box, Button, Card, CardContent, Chip, CircularProgress, Stack, Typography } from "@mui/material";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import WhatshotIcon from "@mui/icons-material/Whatshot";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { ChampionshipMatchesList } from "@/features/tournaments/components/ChampionshipMatchesList";
import { ChampionshipStandingsTable } from "@/features/tournaments/components/ChampionshipStandingsTable";
import { useMyChampionship } from "@/hooks/tournaments/useMyChampionship";
import type { ChampionshipMatchSummary, ChampionshipStanding } from "@/types/tournaments";

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

  const standings = data?.standings ?? [];
  const clubPosition = data?.club_position ?? null;

  const userClubRow = useMemo(
    () => standings.find((row) => clubPosition != null && row.position === clubPosition),
    [standings, clubPosition],
  );
  const userTeamId = userClubRow?.team.id ?? null;

  const clubSchedule = useMemo(() => {
    if (!userTeamId) {
      return schedule;
    }
    const filtered = schedule.filter(
      (match) => match.home_team.id === userTeamId || match.away_team.id === userTeamId,
    );
    return filtered.length > 0 ? filtered : schedule;
  }, [schedule, userTeamId]);

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
    clubSchedule.find((match) => new Date(match.date).getTime() >= Date.now()) ??
    (clubSchedule.length > 0 ? clubSchedule[0] : null);
  const nextMatchLabel = nextMatch ? `${nextMatch.home_team.name} vs ${nextMatch.away_team.name}` : "No fixtures";
  const nextMatchDate = nextMatch ? new Date(nextMatch.date).toLocaleString() : "TBD";
  const playedCount = Array.isArray(data.last_results) ? data.last_results.length : 0;
  const upcomingCount = Array.isArray(data.next_matches) ? data.next_matches.length : 0;

  const gapMetric = buildGapToTarget({
    standings: data.standings,
    clubPosition: data.club_position,
    leagueLevel: data.championship.league.level,
  });

  const fixtureDifficulty = buildFixtureDifficulty({
    schedule,
    standings: data.standings,
    clubPosition: data.club_position,
    clubTeamId: userTeamId,
  });
  const fixtureLabel = fixtureDifficulty
    ? `Fixture difficulty · Next ${fixtureDifficulty.matchCount} match${fixtureDifficulty.matchCount === 1 ? "" : "es"}`
    : "Fixture difficulty";

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
        {
          label: fixtureLabel,
          value: fixtureDifficulty?.value ?? "No data",
          icon: <WhatshotIcon fontSize="small" />,
          hint: fixtureDifficulty?.hint,
          badge: fixtureDifficulty?.badge,
          tooltip: fixtureDifficulty?.tooltip,
        },
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

type FixtureDifficultyMetric = {
  value: string;
  hint: ReactNode;
  badge: {
    label: string;
    tone: "success" | "caution" | "warning" | "danger";
  };
  tooltip: string;
  matchCount: number;
};

type GapMetric = {
  value: string;
  hint: ReactNode;
  badge: {
    label: string;
    tone: "success" | "warning" | "danger";
  };
  tooltip: string;
};

function buildFixtureDifficulty({
  schedule,
  standings,
  clubPosition,
  clubTeamId,
}: {
  schedule: ChampionshipMatchSummary[];
  standings: ChampionshipStanding[];
  clubPosition?: number | null;
  clubTeamId?: number | null;
}): FixtureDifficultyMetric | null {
  if (!Array.isArray(schedule) || schedule.length === 0) {
    return null;
  }

  const clubId =
    clubTeamId ??
    standings.find((row) => row.position === clubPosition)?.team.id ??
    null;
  if (!clubId) {
    return null;
  }

  const now = Date.now();
  const upcoming = schedule
    .filter((match) => {
      const matchTime = new Date(match.date).getTime();
      const involvesClub = match.home_team.id === clubId || match.away_team.id === clubId;
      return involvesClub && matchTime >= now;
    })
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 3);

  if (upcoming.length === 0) {
    return null;
  }

  const positionMap = new Map(standings.map((row) => [row.team.id, row.position]));
  const totalTeams =
    standings.length > 0
      ? standings.length
      : Math.max(
          ...schedule
            .map((match) => [match.home_team.id, match.away_team.id])
            .flat()
            .map((teamId) => positionMap.get(teamId) ?? 0),
          1,
        );

  const processed = upcoming.map((match) => {
    const isHome = match.home_team.id === clubId;
    const opponentId = isHome ? match.away_team.id : match.home_team.id;
    const opponentPosition = positionMap.get(opponentId);
    const baseDifficulty =
      opponentPosition && totalTeams > 1 ? positionToDifficulty(opponentPosition, totalTeams) : 3;
    const travelAdjustment = isHome ? -0.2 : 0.3;
    const adjusted = baseDifficulty + travelAdjustment;
    const positionLabel = opponentPosition ?? "?";
    return {
      adjusted,
      isHome,
      positionLabel,
    };
  });

  const availableMatches = processed.length;
  if (availableMatches === 0) {
    return null;
  }

  const average = processed.reduce((sum, item) => sum + item.adjusted, 0) / availableMatches;
  const clamped = Math.min(5, Math.max(1, average));
  const rounded = Math.round(clamped * 2) / 2;
  const formattedScore = rounded.toFixed(1);

  let label: "Easy" | "Moderate" | "Hard" | "Very Hard";
  let tone: "success" | "caution" | "warning" | "danger";
  if (rounded >= 4.5) {
    label = "Very Hard";
    tone = "danger";
  } else if (rounded >= 3.5) {
    label = "Hard";
    tone = "warning";
  } else if (rounded >= 2.5) {
    label = "Moderate";
    tone = "caution";
  } else {
    label = "Easy";
    tone = "success";
  }

  const matchCountLabel = `Next ${availableMatches} match${availableMatches === 1 ? "" : "es"}`;
  const chips = processed.map((item, index) => (
    <span
      key={`${item.positionLabel}-${index}`}
      className="inline-flex items-center gap-1 rounded-full bg-white/20 px-2 py-0.5 text-[11px]"
      title={item.isHome ? "Home" : "Away"}
    >
      <span>{item.isHome ? "🏟" : "✈"}</span>
      <span>{item.positionLabel}</span>
    </span>
  ));
  const hint = (
    <div className="flex flex-wrap items-center gap-2">
      <span>{matchCountLabel}</span>
      <span>·</span>
      <div className="flex flex-wrap gap-1" aria-label="Upcoming opponents (🏟 home / ✈ away)">
        {chips}
      </div>
    </div>
  );

  return {
    value: `${formattedScore} / 5 — ${label}`,
    hint,
    badge: { label, tone },
    tooltip: `${matchCountLabel} difficulty (auto, legend: 🏟 home / ✈ away)`,
    matchCount: availableMatches,
  };
}

function positionToDifficulty(position: number, totalTeams: number): number {
  if (totalTeams <= 1) {
    return 3;
  }
  const normalized = 1 - (position - 1) / (totalTeams - 1);
  return 1 + normalized * 4;
}

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
