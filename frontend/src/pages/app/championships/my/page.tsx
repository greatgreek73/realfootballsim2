import { useEffect, useMemo, useRef, useState } from "react";

import { Link as RouterLink } from "react-router-dom";
import { Alert, Box, Button, Card, CardContent, CircularProgress, Stack, Typography } from "@mui/material";
import { alpha } from "@mui/material/styles";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import WhatshotIcon from "@mui/icons-material/Whatshot";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { ChampionshipStandingsTable } from "@/features/tournaments/components/ChampionshipStandingsTable";
import { useMyChampionship } from "@/hooks/tournaments/useMyChampionship";
import type { ChampionshipMatchSummary, ChampionshipStanding } from "@/types/tournaments";
import {
  buildFixtureDifficulty,
  buildGapToTarget,
  describeMatchStatus,
  determineCurrentRound,
  formatDateTime,
  formatOrdinal,
  getResultBadge,
  groupMatchesByRound,
  type RoundGroup,
} from "./utils";

type ClubRound = RoundGroup & {
  clubMatch: ChampionshipMatchSummary;
};

export default function MyChampionshipPage() {
  const { data, loading, error } = useMyChampionship();
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

  const clubSchedule = useMemo(() => {
    if (!userTeamId) {
      return schedule;
    }
    const filtered = schedule.filter(
      (match) => match.home_team.id === userTeamId || match.away_team.id === userTeamId,
    );
    return filtered.length > 0 ? filtered : schedule;
  }, [schedule, userTeamId]);

  const positionMap = useMemo(
    () => new Map(standings.map((row) => [row.team.id, row.position])),
    [standings],
  );

  const roundGroups = useMemo(() => groupMatchesByRound(schedule), [schedule]);

  const clubRounds = useMemo<ClubRound[]>(() => {
    if (roundGroups.length === 0) {
      return [];
    }

    const entries = roundGroups
      .map<ClubRound | null>((round) => {
        const clubMatch =
          userTeamId != null
            ? round.matches.find(
                (match) => match.home_team.id === userTeamId || match.away_team.id === userTeamId,
              )
            : round.matches[0];
        if (!clubMatch) {
          return null;
        }
        return {
          ...round,
          clubMatch,
        };
      })
      .filter((entry): entry is ClubRound => Boolean(entry));

    if (entries.length > 0) {
      return entries;
    }

    return roundGroups
      .map((round) => (round.matches[0] ? { ...round, clubMatch: round.matches[0] } : null))
      .filter((entry): entry is ClubRound => Boolean(entry));
  }, [roundGroups, userTeamId]);

  const currentRoundNumber = useMemo(() => determineCurrentRound(schedule, Date.now()), [schedule]);
  const [expandedRound, setExpandedRound] = useState<number | null>(null);
  const roundRefs = useRef<Record<number, HTMLDivElement | null>>({});
  const autoScrolledRef = useRef(false);

  useEffect(() => {
    if (autoScrolledRef.current) {
      return;
    }
    if (!currentRoundNumber) {
      return;
    }
    const node = roundRefs.current[currentRoundNumber];
    if (node) {
      node.scrollIntoView({ behavior: "smooth", block: "center" });
      autoScrolledRef.current = true;
    }
  }, [currentRoundNumber, clubRounds.length]);

  const handleRoundToggle = (round: number) => {
    setExpandedRound((prev) => (prev === round ? null : round));
  };

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
  const nextMatchDate = nextMatch ? formatDateTime(nextMatch.date) : "TBD";
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
      <CardContent sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Typography variant="h6">Rounds — My club</Typography>
        {clubRounds.length === 0 ? (
          <Typography variant="body2">
            {userTeamId ? "No fixtures available for your club." : "No fixtures available."}
          </Typography>
        ) : (
          <Stack spacing={1.5} sx={{ maxHeight: { md: 600 }, overflowY: "auto", pr: 1 }}>
            {clubRounds.map((roundEntry) => {
              const { round, dateRange, matches, clubMatch } = roundEntry;
              const isCurrentRound = currentRoundNumber === round;
              const badge = getResultBadge(clubMatch, userTeamId);
              const statusColor = toneToColor(badge.tone);
              const isFutureMatch =
                clubMatch.status === "scheduled" || clubMatch.status === "in_progress";
              const opponentTeam =
                userTeamId != null
                  ? clubMatch.home_team.id === userTeamId
                    ? clubMatch.away_team
                    : clubMatch.home_team
                  : null;
              const opponentPosition = opponentTeam ? positionMap.get(opponentTeam.id) : undefined;

              return (
                <Stack
                  key={round}
                  spacing={expandedRound === round ? 1.25 : 0.75}
                  ref={(node) => {
                    roundRefs.current[round] = node;
                  }}
                  sx={(theme) => ({
                    borderRadius: 2,
                    border: "1px solid",
                    borderColor: isCurrentRound ? theme.palette.primary.main : "divider",
                    backgroundColor: isCurrentRound
                      ? alpha(theme.palette.primary.main, 0.08)
                      : "transparent",
                    p: 1.5,
                  })}
                >
                  <Stack
                    direction="row"
                    spacing={1.5}
                    alignItems="center"
                    justifyContent="space-between"
                    onClick={() => handleRoundToggle(round)}
                    sx={{ cursor: "pointer" }}
                  >
                    <Stack spacing={0.5} sx={{ flexGrow: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Round {round} · {dateRange}
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {renderTeamLabel(
                          clubMatch.home_team,
                          userTeamId,
                          opponentTeam,
                          opponentPosition,
                        )}{" "}
                        –{" "}
                        {renderTeamLabel(
                          clubMatch.away_team,
                          userTeamId,
                          opponentTeam,
                          opponentPosition,
                        )}
                      </Typography>
                      <Typography variant="caption" sx={{ color: statusColor }}>
                        {badge.label}
                      </Typography>
                    </Stack>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Button
                        component={RouterLink}
                        to={`/matches/${clubMatch.match_id}`}
                        size="small"
                        variant={isFutureMatch ? "contained" : "outlined"}
                        color={isFutureMatch ? "primary" : "inherit"}
                        onClick={(event) => event.stopPropagation()}
                      >
                        View
                      </Button>
                      <ExpandMoreIcon
                        fontSize="small"
                        sx={{
                          transition: "transform 0.2s ease",
                          transform: expandedRound === round ? "rotate(180deg)" : "rotate(0deg)",
                        }}
                      />
                    </Stack>
                  </Stack>

                  {expandedRound === round && (
                    <Stack spacing={1}>
                      {matches.map((match) => {
                        const isClubMatch =
                          userTeamId != null &&
                          (match.home_team.id === userTeamId || match.away_team.id === userTeamId);
                        return (
                          <Stack
                            key={match.id}
                            direction="row"
                            spacing={1}
                            alignItems="center"
                            justifyContent="space-between"
                            sx={(theme) => ({
                              borderRadius: 1.5,
                              p: 1,
                              backgroundColor: isClubMatch
                                ? alpha(theme.palette.primary.main, 0.08)
                                : "transparent",
                            })}
                          >
                            <Stack spacing={0.25} sx={{ flexGrow: 1 }}>
                              <Typography variant="body2" fontWeight={isClubMatch ? 600 : 500}>
                                {match.home_team.name} – {match.away_team.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {describeMatchStatus(match)}
                              </Typography>
                            </Stack>
                            <Button
                              component={RouterLink}
                              to={`/matches/${match.match_id}`}
                              size="small"
                              variant="text"
                              onClick={(event) => event.stopPropagation()}
                            >
                              View
                            </Button>
                          </Stack>
                        );
                      })}
                    </Stack>
                  )}
                </Stack>
              );
            })}
          </Stack>
        )}
        <Button
          component={RouterLink}
          to="/championships/my/schedule"
          size="small"
          variant="text"
          endIcon={<ArrowForwardIcon fontSize="small" />}
          sx={{ alignSelf: { md: "flex-end" } }}
        >
          Full schedule
        </Button>
      </CardContent>
    </Card>
  );
  return <PageShell hero={hero} main={mainContent} aside={asideContent} />;
}

function renderTeamLabel(
  team: ChampionshipMatchSummary["home_team"],
  userTeamId?: number | null,
  opponentTeam?: ChampionshipMatchSummary["home_team"] | ChampionshipMatchSummary["away_team"] | null,
  opponentPosition?: number,
) {
  const isUserTeam = userTeamId != null && team.id === userTeamId;
  const isOpponent = opponentTeam && opponentTeam.id === team.id && opponentPosition != null;
  return (
    <Box
      component="span"
      sx={{
        fontWeight: isUserTeam ? 700 : 500,
        color: isUserTeam ? "text.primary" : "text.secondary",
      }}
    >
      {team.name}
      {isOpponent ? ` (${formatOrdinal(opponentPosition as number)})` : ""}
    </Box>
  );
}

function toneToColor(tone: "success" | "error" | "warning" | "info" | "default"): string {
  switch (tone) {
    case "success":
      return "success.main";
    case "error":
      return "error.main";
    case "warning":
      return "warning.main";
    case "info":
      return "info.main";
    default:
      return "text.secondary";
  }
}


