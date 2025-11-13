import { useEffect, useMemo, useState } from "react";

import { Link as RouterLink } from "react-router-dom";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  FormControlLabel,
  MenuItem,
  Stack,
  Switch,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import type { SelectChangeEvent } from "@mui/material/Select";
import { alpha } from "@mui/material/styles";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import WhatshotIcon from "@mui/icons-material/Whatshot";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { useMyChampionship } from "@/hooks/tournaments/useMyChampionship";
import type { ChampionshipMatchSummary } from "@/types/tournaments";
import {
  buildFixtureDifficulty,
  buildGapToTarget,
  describeMatchStatus,
  determineCurrentRound,
  formatDateTime,
  formatOrdinal,
  groupMatchesByRound,
  isUpcomingMatch,
} from "../utils";

type ShowFilter = "upcoming" | "all";

export default function MyChampionshipSchedulePage() {
  const { data, loading, error } = useMyChampionship();
  const [onlyMyClub, setOnlyMyClub] = useState(true);
  const [showFilter, setShowFilter] = useState<ShowFilter>("upcoming");
  const [expandedRounds, setExpandedRounds] = useState<number[]>([]);
  const [initialised, setInitialised] = useState(false);
  const [jumpValue, setJumpValue] = useState("");

  const schedule = useMemo(() => {
    if (!data) return [];
    const base = Array.isArray(data.schedule) ? data.schedule : [];
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

  useEffect(() => {
    if (!userTeamId) {
      setOnlyMyClub(false);
    }
  }, [userTeamId]);

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

  const gapMetric = buildGapToTarget({
    standings,
    clubPosition: data.club_position,
    leagueLevel: data.championship.league.level,
  });

  const nextMatch =
    schedule.find((match) => new Date(match.date).getTime() >= Date.now()) ??
    (schedule.length > 0 ? schedule[0] : null);
  const nextMatchLabel = nextMatch ? `${nextMatch.home_team.name} vs ${nextMatch.away_team.name}` : "No fixtures";
  const nextMatchDate = nextMatch ? formatDateTime(nextMatch.date) : "TBD";

  const fixtureDifficulty = buildFixtureDifficulty({
    schedule,
    standings,
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
        {
          label: "Position",
          value: data.club_position ?? "-",
          hint: "Current standing",
          icon: <LeaderboardIcon fontSize="small" />,
        },
        {
          label: "Gap to target",
          value: gapMetric?.value ?? "No data",
          icon: <TrendingUpIcon fontSize="small" />,
          hint: gapMetric?.hint,
          badge: gapMetric?.badge,
          tooltip: gapMetric?.tooltip,
        },
        {
          label: "Next game",
          value: nextMatchDate,
          hint: nextMatchLabel,
          icon: <EventAvailableIcon fontSize="small" />,
        },
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
        <Button
          component={RouterLink}
          to="/championships/my"
          size="small"
          variant="outlined"
          startIcon={<ArrowBackIcon fontSize="small" />}
        >
          Back to overview
        </Button>
      }
    />
  );

  const positionMap = useMemo(
    () => new Map(standings.map((row) => [row.team.id, row.position])),
    [standings],
  );

  const groupedRounds = useMemo(() => groupMatchesByRound(schedule), [schedule]);
  const now = Date.now();

  const defaultExpanded = useMemo(() => {
    if (groupedRounds.length === 0) {
      return [];
    }
    const base = determineCurrentRound(schedule, now);
    const upcomingRound = schedule.find((match) => isUpcomingMatch(match, now))?.round ?? null;
    return Array.from(
      new Set(
        [base, upcomingRound].filter((value): value is number => typeof value === "number"),
      ),
    );
  }, [schedule, groupedRounds, now]);
  useEffect(() => {
    if (!initialised && defaultExpanded.length > 0) {
      setExpandedRounds(defaultExpanded);
      setInitialised(true);
    }
  }, [defaultExpanded, initialised]);

  const visibleRounds = useMemo(
    () =>
      groupedRounds.filter((group) =>
        showFilter === "all" ? true : group.matches.some((match) => isUpcomingMatch(match, now)),
      ),
    [groupedRounds, showFilter, now],
  );

  const handleToggleRound = (round: number) => {
    setExpandedRounds((prev) =>
      prev.includes(round) ? prev.filter((item) => item !== round) : [...prev, round],
    );
  };

  const handleJumpChange = (event: SelectChangeEvent<string>) => {
    const { value } = event.target;
    setJumpValue(value);
    if (!value) return;
    const roundNumber = Number(value);
    if (Number.isNaN(roundNumber)) return;
    setExpandedRounds((prev) => (prev.includes(roundNumber) ? prev : [...prev, roundNumber]));
    if (typeof window !== "undefined") {
      requestAnimationFrame(() => {
        const el = document.getElementById(`round-${roundNumber}`);
        el?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  };

  const controls = (
    <Stack
      direction={{ xs: "column", md: "row" }}
      spacing={2}
      alignItems={{ xs: "flex-start", md: "center" }}
      flexWrap="wrap"
    >
      <FormControlLabel
        control={
          <Switch
            checked={onlyMyClub}
            onChange={(event) => setOnlyMyClub(event.target.checked)}
            disabled={!userTeamId}
          />
        }
        label="My club only"
      />
      <Stack direction="row" spacing={1} alignItems="center">
        <Typography variant="body2" fontWeight={600}>
          Show:
        </Typography>
        <ToggleButtonGroup
          exclusive
          size="small"
          value={showFilter}
          onChange={(_, value: ShowFilter | null) => value && setShowFilter(value)}
        >
          <ToggleButton value="upcoming">Upcoming</ToggleButton>
          <ToggleButton value="all">All season</ToggleButton>
        </ToggleButtonGroup>
      </Stack>
      <TextField
        select
        size="small"
        label="Jump to round"
        value={jumpValue}
        onChange={handleJumpChange}
        sx={{ minWidth: 220 }}
      >
        <MenuItem value="">
          <em>None</em>
        </MenuItem>
        {groupedRounds.map((group) => (
          <MenuItem key={group.round} value={group.round}>
            Round {group.round}
          </MenuItem>
        ))}
      </TextField>
    </Stack>
  );

  const scheduleList = (
    <Stack spacing={1.5}>
      {visibleRounds.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No rounds match the selected filters.
        </Typography>
      ) : (
        visibleRounds.map((group) => {
          const matchesToShow = group.matches.filter((match) => {
            if (showFilter === "upcoming" && !isUpcomingMatch(match, now)) {
              return false;
            }
            if (onlyMyClub && userTeamId) {
              return match.home_team.id === userTeamId || match.away_team.id === userTeamId;
            }
            return true;
          });
          const hasMatches = matchesToShow.length > 0;
          return (
            <Accordion
              key={group.round}
              expanded={expandedRounds.includes(group.round)}
              onChange={() => handleToggleRound(group.round)}
              id={`round-${group.round}`}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight={600}>
                  Round {group.round} — {group.dateRange}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {hasMatches ? (
                  <Stack spacing={1.5}>
                    {matchesToShow.map((match) => {
                      const isClubMatch =
                        userTeamId != null &&
                        (match.home_team.id === userTeamId || match.away_team.id === userTeamId);
                      const perspectiveTeamId = userTeamId ?? null;
                      const isHome = perspectiveTeamId ? match.home_team.id === perspectiveTeamId : false;
                      const opponent =
                        perspectiveTeamId == null
                          ? null
                          : isHome
                          ? match.away_team
                          : match.home_team;
                      const opponentPosition = opponent ? positionMap.get(opponent.id) : undefined;
                      const opponentLabel =
                        opponent && opponentPosition
                          ? `${opponent.name} (${formatOrdinal(opponentPosition)})`
                          : opponent?.name;
                      return (
                        <Stack
                          key={match.id}
                          direction={{ xs: "column", md: "row" }}
                          spacing={1}
                          alignItems={{ xs: "flex-start", md: "center" }}
                          justifyContent="space-between"
                          sx={(theme) => ({
                            borderRadius: 1.5,
                            border: "1px solid",
                            borderColor: isClubMatch ? theme.palette.primary.main : "divider",
                            backgroundColor: isClubMatch ? alpha(theme.palette.primary.main, 0.08) : "transparent",
                            p: 1.5,
                          })}
                        >
                          <Stack spacing={0.5} sx={{ flexGrow: 1 }}>
                            <Typography variant="subtitle2" fontWeight={600}>
                              {match.home_team.name} vs {match.away_team.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {formatDateTime(match.date)}
                              {opponentLabel ? ` · ${isHome ? "Home" : "Away"} vs ${opponentLabel}` : ""}
                            </Typography>
                            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                              <StatusChip status={match.status} />
                              <Typography variant="body2" color="text.secondary">
                                {describeMatchStatus(match)}
                              </Typography>
                            </Stack>
                          </Stack>
                          <Button
                            component={RouterLink}
                            to={`/matches/${match.match_id}`}
                            size="small"
                            variant={isClubMatch ? "contained" : "outlined"}
                            color={isClubMatch ? "primary" : "inherit"}
                          >
                            View
                          </Button>
                        </Stack>
                      );
                    })}
                  </Stack>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    {onlyMyClub && userTeamId
                      ? "Your club has no matches in this round."
                      : "No matches fit the current filters."}
                  </Typography>
                )}
              </AccordionDetails>
            </Accordion>
          );
        })
      )}
    </Stack>
  );

  const mainContent = (
    <Card sx={{ minWidth: 0 }}>
      <CardContent>
        <Stack spacing={3}>
          <Typography variant="h6">Season schedule</Typography>
          {controls}
          {scheduleList}
        </Stack>
      </CardContent>
    </Card>
  );

  return <PageShell hero={hero} main={mainContent} />;
}

function StatusChip({ status }: { status: ChampionshipMatchSummary["status"] }) {
  let color: "default" | "primary" | "success" | "warning" | "info" | "error" = "default";
  let label = status.replace("_", " ");
  switch (status) {
    case "finished":
      color = "success";
      label = "Finished";
      break;
    case "in_progress":
      color = "warning";
      label = "Live";
      break;
    case "cancelled":
    case "error":
      color = "error";
      break;
    case "scheduled":
      color = "info";
      break;
    default:
      color = "default";
      break;
  }
  return <Chip size="small" color={color} label={label} />;
}


