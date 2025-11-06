
import { Alert, Box, Card, CardContent, CircularProgress, Stack, Typography } from "@mui/material";

import { ChampionshipMatchesList } from "@/features/tournaments/components/ChampionshipMatchesList";
import { ChampionshipStandingsTable } from "@/features/tournaments/components/ChampionshipStandingsTable";
import { useMyChampionship } from "@/hooks/tournaments/useMyChampionship";

export default function MyChampionshipPage() {
  const { data, loading, error } = useMyChampionship();

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
    return <Alert severity="info">Для вашего клуба не найден активный чемпионат.</Alert>;
  }

  return (
    <Stack spacing={3}>
      <Card>
        <CardContent>
          <Typography variant="h4" sx={{ mb: 1 }}>
            {data.championship.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {data.championship.league.name} • {data.championship.season.name}
          </Typography>
          <Typography variant="body2">Ваша позиция: {data.club_position}</Typography>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Турнирная таблица
          </Typography>
          <ChampionshipStandingsTable standings={data.standings} />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Ближайшие матчи
          </Typography>
          <ChampionshipMatchesList matches={data.next_matches} showRound={false} />
        </CardContent>
      </Card>

      {data.last_results.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Последние результаты
            </Typography>
            <ChampionshipMatchesList matches={data.last_results} showRound={false} />
          </CardContent>
        </Card>
      )}
    </Stack>
  );
}
