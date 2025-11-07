import { useMemo } from "react";

import { Alert, Box, Card, CardContent, CircularProgress, Stack, Typography } from "@mui/material";

import { ChampionshipMatchesList } from "@/features/tournaments/components/ChampionshipMatchesList";
import { ChampionshipStandingsTable } from "@/features/tournaments/components/ChampionshipStandingsTable";
import { useMyChampionship } from "@/hooks/tournaments/useMyChampionship";

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

  return (
    <Stack spacing={3}>
      <Card>
        <CardContent>
          <Typography variant="h4" sx={{ mb: 1 }}>
            {data.championship.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {data.championship.league.name} · {data.championship.season.name}
          </Typography>
          <Typography variant="body2">Your position: {data.club_position ?? "—"}</Typography>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Standings
          </Typography>
          <ChampionshipStandingsTable standings={data.standings} />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Season schedule
          </Typography>
          {schedule.length === 0 ? (
            <Typography variant="body2">No fixtures available.</Typography>
          ) : (
            <ChampionshipMatchesList matches={schedule} />
          )}
        </CardContent>
      </Card>
    </Stack>
  );
}
