
import { ReactNode, useMemo, useState } from "react";

import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import PublicIcon from "@mui/icons-material/Public";
import FilterAltIcon from "@mui/icons-material/FilterAlt";
import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";

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

  const selectedSeasonLabel =
    seasonFilter != null
      ? seasonOptions.find((season) => season.id === seasonFilter)?.name ?? `Season ${seasonFilter}`
      : "All seasons";
  const selectedLeagueLabel =
    leagueFilter != null
      ? leagueOptions.find((league) => league.id === leagueFilter)?.name ?? `League ${leagueFilter}`
      : "All leagues";
  const activeFiltersCount = [seasonFilter, leagueFilter].filter(Boolean).length;

  const hero = (
    <HeroBar
      title="Championship Explorer"
      subtitle="Отслеживайте активные турниры по сезонам и лигам"
      tone="teal"
      kpis={[
        { label: "Tournaments", value: data?.length ?? 0, icon: <EmojiEventsIcon fontSize="small" /> },
        { label: "Seasons", value: seasonOptions.length || "-", icon: <CalendarMonthIcon fontSize="small" /> },
        { label: "Leagues", value: leagueOptions.length || "-", icon: <PublicIcon fontSize="small" /> },
        {
          label: "Filters",
          value: activeFiltersCount === 0 ? "None" : activeFiltersCount,
          icon: <FilterAltIcon fontSize="small" />,
          hint: `${selectedSeasonLabel} · ${selectedLeagueLabel}`,
        },
      ]}
      accent={
        <Stack direction={{ xs: "column", md: "row" }} spacing={1} flexWrap="wrap">
          <Chip
            label={`Season: ${selectedSeasonLabel}`}
            size="small"
            sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
          />
          <Chip
            label={`League: ${selectedLeagueLabel}`}
            size="small"
            sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
          />
        </Stack>
      }
    />
  );

  const filters = (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <div>
            <Typography variant="subtitle1" fontWeight={600}>
              Быстрые фильтры
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Выберите сезон и лигу, чтобы сфокусироваться на нужном турнире
            </Typography>
          </div>
          <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
            <Select
              size="small"
              displayEmpty
              value={seasonFilter ?? ""}
              onChange={(event) => setSeasonFilter(event.target.value ? Number(event.target.value) : undefined)}
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
              onChange={(event) => setLeagueFilter(event.target.value ? Number(event.target.value) : undefined)}
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
        </Stack>
      </CardContent>
    </Card>
  );

  let mainContent: ReactNode;
  if (loading) {
    mainContent = (
      <Stack sx={{ alignItems: "center", py: 6 }}>
        <CircularProgress />
      </Stack>
    );
  } else if (error) {
    mainContent = <Alert severity="error">{error}</Alert>;
  } else if (!data || data.length === 0) {
    mainContent = <Alert severity="info">Чемпионаты не найдены.</Alert>;
  } else {
    mainContent = (
      <Grid container spacing={3}>
        {data.map((championship) => (
          <Grid key={championship.id} item xs={12} md={6} lg={4}>
            <ChampionshipCard championship={championship} />
          </Grid>
        ))}
      </Grid>
    );
  }

  return <PageShell hero={hero} top={filters} main={mainContent} />;
}
