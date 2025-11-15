import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  ButtonGroup,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import TimelineIcon from "@mui/icons-material/Timeline";
import FlagCircleIcon from "@mui/icons-material/FlagCircle";
import SportsSoccerIcon from "@mui/icons-material/SportsSoccer";

import {
  ChampionshipMatchesList,
  MATCH_STATUS_LABELS,
} from "@/features/tournaments/components/ChampionshipMatchesList";
import { ChampionshipStandingsTable } from "@/features/tournaments/components/ChampionshipStandingsTable";
import { useChampionshipDetail } from "@/hooks/tournaments/useChampionshipDetail";
import type { ChampionshipMatchSummary, ChampionshipStanding } from "@/types/tournaments";
import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";

type ChampionshipTabs = "standings" | "fixtures" | "calendar";

function groupMatchesByDate(matches: ChampionshipMatchSummary[]) {
  const map = new Map<string, ChampionshipMatchSummary[]>();
  matches.forEach((match) => {
    const bucket = map.get(match.date) ?? [];
    bucket.push(match);
    map.set(match.date, bucket);
  });
  return Array.from(map.entries())
    .sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
    .map(([date, groupedMatches]) => ({
      date,
      matches: groupedMatches.sort(
        (left, right) => new Date(left.date).getTime() - new Date(right.date).getTime(),
      ),
    }));
}

export default function ChampionshipDetailPage() {
  const { championshipId } = useParams<{ championshipId: string }>();
  const numericId = useMemo(() => {
    if (!championshipId) return null;
    const parsed = Number(championshipId);
    return Number.isFinite(parsed) ? parsed : null;
  }, [championshipId]);
  const { detail, matches, loading, error } = useChampionshipDetail(numericId);
  const [tab, setTab] = useState<ChampionshipTabs>("standings");
  const [roundFilter, setRoundFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const standings = useMemo(
    () => (Array.isArray(detail?.standings) ? detail.standings : []),
    [detail],
  );
  const matchesList = useMemo(
    () =>
      Array.isArray(matches)
        ? matches.filter(
            (match): match is ChampionshipMatchSummary =>
              Boolean(match && match.date && match.home_team && match.away_team),
          )
        : [],
    [matches],
  );
  const availableRounds = useMemo(() => {
    const unique = new Set<number>();
    matchesList.forEach((match) => unique.add(match.round));
    return Array.from(unique).sort((a, b) => a - b);
  }, [matchesList]);
  const availableStatuses = useMemo(() => {
    const unique = new Set(matchesList.map((match) => match.status));
    return Array.from(unique);
  }, [matchesList]);
  const filteredMatches = useMemo(() => {
    return matchesList.filter((match) => {
      const roundPass = roundFilter === "all" || match.round === Number(roundFilter);
      const statusPass = statusFilter === "all" || match.status === statusFilter;
      return roundPass && statusPass;
    });
  }, [matchesList, roundFilter, statusFilter]);
  const groupedMatches = useMemo(() => groupMatchesByDate(filteredMatches), [filteredMatches]);

  if (!numericId) {
    return <Alert severity="warning">Invalid championship id.</Alert>;
  }

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

  if (!detail) {
    return <Alert severity="info">Championship not found.</Alert>;
  }

  const heroActions = (
    <ButtonGroup variant="outlined" size="small">
      <Button variant={tab === "standings" ? "contained" : "outlined"} onClick={() => setTab("standings")}>
        Table
      </Button>
      <Button variant={tab === "fixtures" ? "contained" : "outlined"} onClick={() => setTab("fixtures")}>
        Matches
      </Button>
      <Button variant={tab === "calendar" ? "contained" : "outlined"} onClick={() => setTab("calendar")}>
        Calendar
      </Button>
    </ButtonGroup>
  );

  const statusLabel =
    detail.championship.status === "pending"
      ? "Not started"
      : detail.championship.status === "in_progress"
      ? "In progress"
      : "Finished";
  const statusSummary = statusFilter === "all" ? "All statuses" : MATCH_STATUS_LABELS[statusFilter] ?? statusFilter;

  const totalRounds = availableRounds.length;
  const finishedStatuses = new Set(["finished", "expired"]);
  let lastFinishedRound = 0;
  let nextRoundCandidate = Number.POSITIVE_INFINITY;
  let finishedMatches = 0;
  matchesList.forEach((match) => {
    if (finishedStatuses.has(match.status)) {
      finishedMatches += 1;
      if (match.round > lastFinishedRound) {
        lastFinishedRound = match.round;
      }
    } else if (match.round < nextRoundCandidate) {
      nextRoundCandidate = match.round;
    }
  });
  const currentRoundValue =
    lastFinishedRound > 0
      ? lastFinishedRound
      : Number.isFinite(nextRoundCandidate)
      ? nextRoundCandidate
      : 1;
  const totalMatches = matchesList.length;
  const goalStats = matchesList.reduce(
    (acc, match) => {
      if (match.score) {
        acc.gamesWithScore += 1;
        acc.totalGoals += match.score.home + match.score.away;
      }
      return acc;
    },
    { totalGoals: 0, gamesWithScore: 0 },
  );
  const avgGoals =
    goalStats.gamesWithScore > 0 ? goalStats.totalGoals / goalStats.gamesWithScore : null;
  const hero = (
    <HeroBar
      title={detail.championship.name}
      subtitle={`${detail.championship.league.name} · ${detail.championship.season.name} overview`}
      tone="orange"
      kpis={[
        { label: "Season", value: detail.championship.season.name, icon: <CalendarMonthIcon fontSize="small" /> },
        {
          label: "Status",
          value: statusLabel,
          icon: <TimelineIcon fontSize="small" />,
          hint: detail.championship.status === "in_progress" ? "Live competition" : statusSummary,
        },
        {
          label: "Progress",
          value: totalRounds
            ? `Round ${currentRoundValue} / ${totalRounds}`
            : `Round ${currentRoundValue}`,
          icon: <FlagCircleIcon fontSize="small" />,
          hint:
            totalMatches > 0
              ? `Played ${finishedMatches} / ${totalMatches} games`
              : undefined,
        },
        {
          label: "Scoring",
          value: avgGoals != null ? `${avgGoals.toFixed(1)} goals/gm` : "No data",
          icon: <SportsSoccerIcon fontSize="small" />,
          hint:
            goalStats.totalGoals > 0
              ? `Total goals: ${goalStats.totalGoals}`
              : undefined,
        },
      ]}
      actions={heroActions}
    />
  );

  const filtersCard =
    tab === "fixtures" ? (
      <Card>
        <CardContent>
          <Stack spacing={2}>
            <div>
              <Typography variant="subtitle1" fontWeight={600}>
                Fixture filters
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ограничьте список по туру и статусу, чтобы быстрее найти нужный матч
              </Typography>
            </div>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <FormControl size="small" sx={{ minWidth: 160 }}>
                <InputLabel id="round-filter-label">Round</InputLabel>
                <Select
                  labelId="round-filter-label"
                  value={roundFilter}
                  label="Round"
                  onChange={(event) => setRoundFilter(event.target.value)}
                >
                  <MenuItem value="all">All rounds</MenuItem>
                  {availableRounds.map((round) => (
                    <MenuItem key={round} value={round}>
                      Round {round}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 180 }}>
                <InputLabel id="status-filter-label">Status</InputLabel>
                <Select
                  labelId="status-filter-label"
                  value={statusFilter}
                  label="Status"
                  onChange={(event) => setStatusFilter(event.target.value)}
                >
                  <MenuItem value="all">All statuses</MenuItem>
                  {availableStatuses.map((status) => {
                    const label = MATCH_STATUS_LABELS[status] ?? status;
                    return (
                      <MenuItem key={status} value={status}>
                        {label}
                      </MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    ) : null;

  const topSection = filtersCard ? <Stack spacing={3}>{filtersCard}</Stack> : undefined;

  const asideContent = (
    <Stack
      spacing={2}
      sx={{
        position: { lg: "sticky" },
        top: { lg: 96 },
      }}
    >
      <KeyFixturesCard standings={standings} matches={matchesList} />
      <TopScorersCard />
    </Stack>
  );

  return (
    <PageShell
      hero={hero}
      top={topSection}
      main={
        <Card>
          <CardContent>
            {tab === "standings" && <ChampionshipStandingsTable standings={standings} />}

            {tab === "fixtures" && <ChampionshipMatchesList matches={filteredMatches} />}

            {tab === "calendar" && (
              <Stack spacing={2}>
                {groupedMatches.length === 0 ? (
                  <Typography variant="body2">No fixtures for the selected filters.</Typography>
                ) : (
                  groupedMatches.map((group) => (
                    <Stack key={group.date} spacing={1.5}>
                      <Typography variant="subtitle2" color="text.secondary">
                        {group.date}
                      </Typography>
                      <Stack spacing={1}>
                        {group.matches.map((match) => (
                          <Stack
                            key={match.id}
                            direction={{ xs: "column", sm: "row" }}
                            spacing={2}
                            alignItems={{ xs: "flex-start", sm: "center" }}
                          >
                            <Typography flex={1}>
                              {match.home_team.name} - {match.away_team.name}
                            </Typography>
                            <Typography width={120}>{match.status}</Typography>
                            <Typography width={80} textAlign="right">
                              {match.score ? `${match.score.home}:${match.score.away}` : "-"}
                            </Typography>
                          </Stack>
                        ))}
                      </Stack>
                      <Divider />
                    </Stack>
                  ))
                )}
              </Stack>
            )}
          </CardContent>
        </Card>
      }
      aside={asideContent}
    />
  );
}

function KeyFixturesCard({
  standings,
  matches,
}: {
  standings: ChampionshipStanding[];
  matches: ChampionshipMatchSummary[];
}) {
  const topTeamIds = new Set(standings.slice(0, 4).map((row) => row.team.id));
  const relegationIds = new Set(
    standings.filter((row) => row.is_relegation_zone).map((row) => row.team.id),
  );

  const upcoming = matches
    .filter((match) => match.status !== "finished")
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  const highlighted = upcoming
    .map((match) => {
      const homeTop = topTeamIds.has(match.home_team.id);
      const awayTop = topTeamIds.has(match.away_team.id);
      const homeReleg = relegationIds.has(match.home_team.id);
      const awayReleg = relegationIds.has(match.away_team.id);
      const isTitleRace = homeTop && awayTop;
      const isRelegation = homeReleg && awayReleg;
      if (!isTitleRace && !isRelegation) {
        return null;
      }
      return {
        match,
        tag: isTitleRace ? "Title race" : "Relegation",
        color: isTitleRace ? "primary" : "warning",
      } as const;
    })
    .filter((item): item is { match: ChampionshipMatchSummary; tag: string; color: "primary" | "warning" } =>
      Boolean(item),
    )
    .slice(0, 4);

  if (highlighted.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Key fixtures
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No highlighted fixtures right now. Check back later in the season.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Key fixtures
        </Typography>
        <Stack spacing={1.25}>
          {highlighted.map(({ match, tag, color }) => (
            <Stack
              key={match.id}
              direction="row"
              spacing={1}
              alignItems="flex-start"
              justifyContent="space-between"
            >
              <Box flex={1}>
                <Typography variant="body2" fontWeight={600}>
                  {formatMatchDay(match.date)} · {match.home_team.name} – {match.away_team.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatMatchTime(match.date)} · {MATCH_STATUS_LABELS[match.status] ?? match.status}
                </Typography>
              </Box>
              <Chip label={tag} size="small" color={color} />
            </Stack>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}

function TopScorersCard() {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Top scorers
        </Typography>
        <Stack spacing={1}>
          <Typography variant="body2" color="text.secondary">
            Detailed scoring stats are not available yet.
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Mock example:
          </Typography>
          <Stack spacing={0.5}>
            <Typography variant="body2">1. J. Smith — 9 goals</Typography>
            <Typography variant="body2">2. A. Lopez — 8 goals</Typography>
            <Typography variant="body2">3. K. Ivanov — 7 goals</Typography>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}

function formatMatchDay(dateString: string): string {
  const value = new Date(dateString);
  if (Number.isNaN(value.getTime())) {
    return dateString;
  }
  return new Intl.DateTimeFormat(undefined, {
    day: "2-digit",
    month: "short",
  }).format(value);
}

function formatMatchTime(dateString: string): string {
  const value = new Date(dateString);
  if (Number.isNaN(value.getTime())) {
    return "-";
  }
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(value);
}


