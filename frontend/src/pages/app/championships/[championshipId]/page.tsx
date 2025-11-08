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

import {
  ChampionshipMatchesList,
  MATCH_STATUS_LABELS,
} from "@/features/tournaments/components/ChampionshipMatchesList";
import { ChampionshipStandingsTable } from "@/features/tournaments/components/ChampionshipStandingsTable";
import { useChampionshipDetail } from "@/hooks/tournaments/useChampionshipDetail";
import { ChampionshipMatchSummary } from "@/types/tournaments";

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

  return (
    <Stack spacing={3}>
      <Card>
        <CardContent>
          <Stack
            direction={{ xs: "column", md: "row" }}
            spacing={2}
            alignItems={{ xs: "flex-start", md: "center" }}
            justifyContent="space-between"
          >
            <Box>
              <Typography variant="h4" sx={{ mb: 1 }}>
                {detail.championship.name}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                <Chip
                  size="small"
                  color={
                    detail.championship.status === "finished"
                      ? "default"
                      : detail.championship.status === "in_progress"
                      ? "success"
                      : "warning"
                  }
                  label={
                    detail.championship.status === "pending"
                      ? "Not started"
                      : detail.championship.status === "in_progress"
                      ? "In progress"
                      : "Finished"
                  }
                />
                <Typography variant="body2" color="text.secondary">
                  {detail.championship.league.country} - {detail.championship.league.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {detail.championship.season.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {detail.championship.start_date} - {detail.championship.end_date}
                </Typography>
              </Stack>
              {detail.championship.match_time && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
                  Default kick-off time: {detail.championship.match_time}
                </Typography>
              )}
            </Box>

            <ButtonGroup variant="outlined" size="small" sx={{ alignSelf: { xs: "stretch", md: "flex-end" } }}>
              <Button
                variant={tab === "standings" ? "contained" : "outlined"}
                onClick={() => setTab("standings")}
              >
                Table
              </Button>
              <Button
                variant={tab === "fixtures" ? "contained" : "outlined"}
                onClick={() => setTab("fixtures")}
              >
                Matches
              </Button>
              <Button
                variant={tab === "calendar" ? "contained" : "outlined"}
                onClick={() => setTab("calendar")}
              >
                Calendar
              </Button>
            </ButtonGroup>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          {tab === "standings" && <ChampionshipStandingsTable standings={standings} />}
          {tab === "fixtures" && (
            <Stack spacing={2}>
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
              <ChampionshipMatchesList matches={filteredMatches} />
            </Stack>
          )}
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
                            {match.score ? `${match.score.home}:${match.score.away}` : "—"}
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
    </Stack>
  );
}
