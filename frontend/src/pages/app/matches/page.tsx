import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Pagination,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Paper,
} from "@mui/material";
import SportsSoccerIcon from "@mui/icons-material/SportsSoccer";
import ScheduleIcon from "@mui/icons-material/Schedule";
import LoopIcon from "@mui/icons-material/Loop";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";

import { createMatch, fetchMatches, MatchStatus, MatchSummary } from "@/api/matches";

const STATUS_COLOR: Record<MatchStatus, "default" | "info" | "warning" | "success" | "error"> = {
  scheduled: "info",
  in_progress: "warning",
  paused: "warning",
  finished: "success",
  cancelled: "default",
  error: "error",
};

const STATUS_LABELS: Record<MatchStatus, string> = {
  scheduled: "Scheduled",
  in_progress: "In progress",
  paused: "Paused",
  finished: "Finished",
  cancelled: "Cancelled",
  error: "Error",
};

const STATUS_ORDER: MatchStatus[] = ["scheduled", "in_progress", "paused", "finished", "cancelled", "error"];

const DATE_FORMATTER = new Intl.DateTimeFormat(undefined, {
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

function formatDate(value: string | null) {
  if (!value) return "TBD";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return DATE_FORMATTER.format(date);
}

export default function MatchesPage() {
  const [matches, setMatches] = useState<MatchSummary[]>([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({
    totalPages: 1,
    count: 0,
    pageSize: 10,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const navigate = useNavigate();
  const totalPages = useMemo(() => Math.max(pagination.totalPages, 1), [pagination.totalPages]);

  useEffect(() => {
    let cancelled = false;

    async function load(pageNumber: number) {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchMatches({ page: pageNumber });
        if (cancelled) return;
        setMatches(response.results);
        setPagination({
          totalPages: response.total_pages,
          count: response.count,
          pageSize: response.page_size,
        });
        if (response.page !== pageNumber) {
          setPage(response.page);
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message ?? "Failed to load matches");
          setMatches([]);
          setPagination({ totalPages: 1, count: 0, pageSize: 10 });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load(page);
    return () => {
      cancelled = true;
    };
  }, [page]);

  const handlePageChange = (_: React.ChangeEvent<unknown>, newPage: number) => {
    setPage(newPage);
  };

  const handleCreateFriendly = async () => {
    try {
      setCreating(true);
      setActionError(null);
      const match = await createMatch({ autoStart: true, autoOpponent: true });

      navigate(`/matches/${match.id}/live`);
    } catch (e: any) {
      setActionError(e?.message ?? "Failed to create match");
    } finally {
      setCreating(false);
    }
  };

  const heroActions = (
    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
      <Button variant="contained" onClick={() => navigate("/matches/create")}>
        Schedule Match
      </Button>
      <Button variant="outlined" onClick={handleCreateFriendly} disabled={creating}>
        {creating ? "Creating..." : "Quick Friendly"}
      </Button>
    </Stack>
  );

  const statusSummary = useMemo<Record<MatchStatus, number>>(() => {
    const summary: Record<MatchStatus, number> = {
      scheduled: 0,
      in_progress: 0,
      paused: 0,
      finished: 0,
      cancelled: 0,
      error: 0,
    };

    matches.forEach((match) => {
      summary[match.status] += 1;
    });

    return summary;
  }, [matches]);

  const nextKickoff = useMemo<MatchSummary | null>(() => {
    const upcoming = matches
      .filter(
        (match) =>
          match.datetime && match.status !== "finished" && match.status !== "cancelled" && match.status !== "error"
      )
      .map((match) => ({ match, timestamp: new Date(match.datetime!).getTime() }))
      .filter((item) => !Number.isNaN(item.timestamp))
      .sort((a, b) => a.timestamp - b.timestamp);

    return upcoming[0]?.match ?? null;
  }, [matches]);

  const hero = (
    <HeroBar
      title="Matches Control"
      subtitle="Browse upcoming fixtures and quick friendlies"
      tone="orange"
      kpis={[
        { label: "Total", value: pagination.count || "—", icon: <SportsSoccerIcon fontSize="small" /> },
        { label: "On page", value: matches.length || "0", icon: <ScheduleIcon fontSize="small" /> },
        { label: "Page", value: `${page}/${totalPages}`, icon: <LoopIcon fontSize="small" /> },
        { label: "State", value: loading ? "Loading" : error ? "Error" : "Ready", icon: <EventAvailableIcon fontSize="small" /> },
      ]}
      accent={
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {STATUS_ORDER.map((status) => (
            <Chip
              key={status}
              label={`${STATUS_LABELS[status]}: ${statusSummary[status] ?? 0}`}
              size="small"
              sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
            />
          ))}
        </Stack>
      }
      actions={heroActions}
    />
  );

  const TopSection = (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Matches
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Browse upcoming and completed fixtures
            </Typography>
          </Box>
          {error && <Alert severity="error">{error}</Alert>}
          {actionError && <Alert severity="warning">{actionError}</Alert>}
        </Stack>
      </CardContent>
    </Card>
  );

  const MainSection = (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
          <Typography variant="h5" component="h2">
            All Matches
          </Typography>
          {pagination.count > 0 && (
            <Typography variant="body2" color="text.secondary">
              Total: {pagination.count}
            </Typography>
          )}
        </Stack>

        {loading && matches.length === 0 ? (
          <Box className="flex w-full items-center justify-center p-6">
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper} variant="outlined">
            <Table size="medium">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Competition</TableCell>
                  <TableCell>Home</TableCell>
                  <TableCell align="center">Score</TableCell>
                  <TableCell>Away</TableCell>
                  <TableCell align="right">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {matches.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No matches found.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  matches.map((match) => {
                    const competitionName =
                      match.competition?.name ??
                      (match.competition?.season ? `Season ${match.competition.season}` : "Friendly");
                    const roundInfo =
                      match.competition?.round != null
                        ? `Round ${match.competition.round}`
                        : match.competition?.match_day != null
                        ? `Matchday ${match.competition.match_day}`
                        : null;

                    return (
                      <TableRow
                        key={match.id}
                        hover
                        sx={{ cursor: "pointer" }}
                        onClick={() => navigate(`/matches/${match.id}`)}
                      >
                        <TableCell>{formatDate(match.datetime)}</TableCell>
                        <TableCell>
                          <Stack spacing={0.5}>
                            <Typography variant="body2">{competitionName}</Typography>
                            {roundInfo && (
                              <Typography variant="caption" color="text.secondary">
                                {roundInfo}
                              </Typography>
                            )}
                          </Stack>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>
                            {match.home.name}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography variant="body1" fontWeight={700}>
                            {match.score.home} : {match.score.away}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>
                            {match.away.name}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={match.status_label}
                            color={STATUS_COLOR[match.status]}
                            variant="outlined"
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Stack direction="row" justifyContent="center" mt={3}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
            shape="rounded"
            showFirstButton
            showLastButton
          />
        </Stack>
      </CardContent>
    </Card>
  );

  const AsideSection = (
    <Stack spacing={2}>
      <Card>
        <CardContent>
          <Typography variant="subtitle1" component="h3">
            Status overview
          </Typography>
          <Stack spacing={1.5} mt={2}>
            {STATUS_ORDER.map((status) => (
              <Stack key={status} direction="row" justifyContent="space-between" alignItems="center">
                <Chip label={STATUS_LABELS[status]} color={STATUS_COLOR[status]} variant="outlined" size="small" />
                <Typography variant="body2" fontWeight={600}>
                  {statusSummary[status] ?? 0}
                </Typography>
              </Stack>
            ))}
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="subtitle1" component="h3">
            Next kickoff
          </Typography>
          {nextKickoff ? (
            <Stack spacing={1.5} mt={2}>
              <Typography variant="body2" fontWeight={600}>
                {nextKickoff.home.name} vs {nextKickoff.away.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatDate(nextKickoff.datetime)}
              </Typography>
              {nextKickoff.competition?.name && (
                <Typography variant="caption" color="text.secondary">
                  {nextKickoff.competition.name}
                </Typography>
              )}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary" mt={1.5}>
              No upcoming fixtures.
            </Typography>
          )}
        </CardContent>
      </Card>
    </Stack>
  );

  return <PageShell hero={hero} top={TopSection} main={MainSection} aside={AsideSection} />;
}
