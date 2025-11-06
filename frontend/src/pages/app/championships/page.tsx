
import { useMemo, useState } from "react";

import { Alert, Box, CircularProgress, Grid, MenuItem, Select, Stack } from "@mui/material";

import { ChampionshipCard } from "@/features/tournaments/components/ChampionshipCard";
import { useLeagues } from "@/hooks/tournaments/useLeagues";
import { useSeasons } from "@/hooks/tournaments/useSeasons";
import { useChampionshipList } from "@/hooks/tournaments/useChampionshipList";

export default function ChampionshipsPage() {
  const [seasonFilter, setSeasonFilter] = useState<number | undefined>();
  const [leagueFilter, setLeagueFilter] = useState<number | undefined>();
  const { data: seasons, loading: seasonsLoading } = useSeasons();
  const { data: leagues, loading: leaguesLoading } = useLeagues();
  const { data, loading, error } = useChampionshipList({
    seasonId: seasonFilter,
    leagueId: leagueFilter,
  });

  const seasonOptions = useMemo(() => seasons ?? [], [seasons]);
  const leagueOptions = useMemo(() => leagues ?? [], [leagues]);

  return (
    <Box>
      <Stack direction={{ xs: "column", md: "row" }} spacing={2} sx={{ mb: 3 }}>
        <Select
          size="small"
          displayEmpty
          value={seasonFilter ?? ""}
          onChange={(event) =>
            setSeasonFilter(event.target.value ? Number(event.target.value) : undefined)
          }
          disabled={seasonsLoading}
        >
          <MenuItem value="">Все сезоны</MenuItem>
          {seasonOptions.map((season) => (
            <MenuItem key={season.id} value={season.id}>
              {season.name}
            </MenuItem>
          ))}
        </Select>

        <Select
          size="small"
          displayEmpty
          value={leagueFilter ?? ""}
          onChange={(event) =>
            setLeagueFilter(event.target.value ? Number(event.target.value) : undefined)
          }
          disabled={leaguesLoading}
        >
          <MenuItem value="">Все лиги</MenuItem>
          {leagueOptions.map((league) => (
            <MenuItem key={league.id} value={league.id}>
              {league.name}
            </MenuItem>
          ))}
        </Select>
      </Stack>

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : !data || data.length === 0 ? (
        <Alert severity="info">Чемпионаты не найдены.</Alert>
      ) : (
        <Grid container spacing={3}>
          {data.map((championship) => (
            <Grid key={championship.id} item xs={12} md={6} lg={4}>
              <ChampionshipCard championship={championship} />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
