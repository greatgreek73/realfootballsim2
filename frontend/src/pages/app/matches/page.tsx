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

import { createMatch, fetchMatches, MatchStatus, MatchSummary, simulateMatch } from "@/api/matches";

const STATUS_COLOR: Record<MatchStatus, "default" | "info" | "warning" | "success" | "error"> = {
  scheduled: "info",
  in_progress: "warning",
  paused: "warning",
  finished: "success",
  cancelled: "default",
  error: "error",
};

const DATE_FORMATTER = new Intl.DateTimeFormat(undefined, {
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

const SHOULD_AUTO_SIMULATE_FRIENDLY =
  typeof import.meta.env.VITE_AUTO_SIMULATE_FRIENDLY === "string"
    ? import.meta.env.VITE_AUTO_SIMULATE_FRIENDLY.toLowerCase() === "true"
    : false;

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
      let match = await createMatch({ autoStart: true, autoOpponent: true });

      if (SHOULD_AUTO_SIMULATE_FRIENDLY) {
        try {
          const simulation = await simulateMatch(match.id, { mode: "full" });
          match = simulation.match;
        } catch (simulationError: any) {
          // Log the failure but let the user continue with manual controls.
          console.warn("Auto simulation fallback failed", simulationError);
          setActionError(
            simulationError?.message ?? "Failed to auto-simulate match; you may need to use the live controls."
          );
        }
      }

      navigate(`/matches/${match.id}/live`);
    } catch (e: any) {
      setActionError(e?.message ?? "Failed to create match");
    } finally {
      setCreating(false);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 4 } }}>
      <Stack spacing={3}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          alignItems={{ xs: "flex-start", md: "center" }}
          justifyContent="space-between"
        >
          <Box>
            <Typography variant="h1" component="h1" className="mb-0">
              Matches
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Browse upcoming and completed fixtures
            </Typography>
          </Box>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Button variant="contained" onClick={() => navigate("/matches/create")}>
              Schedule Match
            </Button>
            <Button variant="outlined" onClick={handleCreateFriendly} disabled={creating}>
              {creating ? "Creating..." : "Quick Friendly"}
            </Button>
          </Stack>
        </Stack>

        {error && <Alert severity="error">{error}</Alert>}
        {actionError && <Alert severity="warning">{actionError}</Alert>}

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
                          match.competition?.name ?? (match.competition?.season ? `Season ${match.competition.season}` : "Friendly");
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
                              <Chip label={match.status_label} color={STATUS_COLOR[match.status]} variant="outlined" size="small" />
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
      </Stack>
    </Box>
  );
}
