import { useEffect, useMemo, useState } from "react";

import { Link as RouterLink } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  InputAdornment,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import PublicIcon from "@mui/icons-material/Public";
import FilterAltIcon from "@mui/icons-material/FilterAlt";
import SearchIcon from "@mui/icons-material/Search";
import StarIcon from "@mui/icons-material/Star";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { ChampionshipCard } from "@/features/tournaments/components/ChampionshipCard";
import { useChampionshipList } from "@/hooks/tournaments/useChampionshipList";
import { useLeagues } from "@/hooks/tournaments/useLeagues";
import { useMyChampionship } from "@/hooks/tournaments/useMyChampionship";
import { useSeasons } from "@/hooks/tournaments/useSeasons";
import type { ChampionshipSummary } from "@/types/tournaments";

export default function ChampionshipsPage() {
  const [seasonFilter, setSeasonFilter] = useState<number | undefined>();
  const [countryFilter, setCountryFilter] = useState<string | undefined>();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedChampionshipId, setSelectedChampionshipId] = useState<number | null>(null);

  const { data: seasons, loading: seasonsLoading } = useSeasons();
  const { data: leagues, loading: leaguesLoading } = useLeagues();
  const { data, loading, error } = useChampionshipList({
    seasonId: seasonFilter,
    country: countryFilter,
  });
  const {
    data: myChampionshipData,
    loading: myChampionshipLoading,
    error: myChampionshipError,
  } = useMyChampionship();

  const seasonOptions = useMemo(() => seasons ?? [], [seasons]);
  const countryOptions = useMemo(() => {
    if (!leagues) return [];
    const set = new Set(leagues.map((league) => league.country));
    return Array.from(set).sort();
  }, [leagues]);

  const selectedSeasonLabel =
    seasonFilter != null
      ? seasonOptions.find((season) => season.id === seasonFilter)?.name ?? `Season ${seasonFilter}`
      : "All seasons";
  const selectedCountryLabel = countryFilter ?? "All countries";
  const activeFiltersCount = [seasonFilter, countryFilter, searchTerm.trim() ? true : null].filter(Boolean)
    .length;

  const hero = (
    <HeroBar
      title="Championship Explorer"
      subtitle="Browse championships across seasons and leagues"
      tone="teal"
      kpis={[
        { label: "Tournaments", value: data?.length ?? 0, icon: <EmojiEventsIcon fontSize="small" /> },
        { label: "Seasons", value: seasonOptions.length || "-", icon: <CalendarMonthIcon fontSize="small" /> },
        { label: "Countries", value: countryOptions.length || "-", icon: <PublicIcon fontSize="small" /> },
        {
          label: "Filters",
          value: activeFiltersCount === 0 ? "None" : activeFiltersCount,
          icon: <FilterAltIcon fontSize="small" />,
          hint: `${selectedSeasonLabel} · ${selectedCountryLabel}${searchTerm ? ` · Search: “${searchTerm}”` : ""}`,
        },
      ]}
    />
  );

  const myChampionship = myChampionshipData?.championship;
  const filteredChampionships = useMemo(() => {
    if (!data) {
      return [];
    }
    const query = searchTerm.trim().toLowerCase();
    if (!query) {
      return data;
    }
    return data.filter((championship) => {
      const haystack = `${championship.name} ${championship.league.name} ${championship.league.country}`.toLowerCase();
      return haystack.includes(query);
    });
  }, [data, searchTerm]);

  useEffect(() => {
    if (!filteredChampionships.length) {
      setSelectedChampionshipId(null);
      return;
    }
    setSelectedChampionshipId((prev) => {
      if (prev && filteredChampionships.some((item) => item.id === prev)) {
        return prev;
      }
      if (myChampionship && filteredChampionships.some((item) => item.id === myChampionship.id)) {
        return myChampionship.id;
      }
      return filteredChampionships[0].id;
    });
  }, [filteredChampionships, myChampionship]);

  const selectedChampionship =
    filteredChampionships.find((item) => item.id === selectedChampionshipId) ?? null;

  const myChampionshipSection = (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">My championships</Typography>
            {myChampionship && (
              <Chip
                size="small"
                icon={<StarIcon fontSize="small" />}
                label="Joined"
                color="warning"
                sx={{ fontWeight: 600 }}
              />
            )}
          </Stack>

          {myChampionshipLoading ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 3 }}>
              <CircularProgress size={24} />
            </Box>
          ) : myChampionshipError ? (
            <Alert severity="warning">{myChampionshipError}</Alert>
          ) : myChampionship ? (
            <ChampionshipCard championship={myChampionship} />
          ) : (
            <Typography variant="body2" color="text.secondary">
              You are not assigned to any championship yet.
            </Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );

  const filtersToolbar = (
    <Stack spacing={1}>
      <Typography variant="subtitle2" fontWeight={600}>
        Filters
      </Typography>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={1}
        alignItems={{ md: "center" }}
      >
        <Select
          size="small"
          displayEmpty
          value={seasonFilter ?? ""}
          onChange={(event) =>
            setSeasonFilter(event.target.value ? Number(event.target.value) : undefined)
          }
          disabled={seasonsLoading}
          sx={{ minWidth: { xs: "100%", md: 160 } }}
        >
          <MenuItem value="">All seasons</MenuItem>
          {seasonOptions.map((season) => (
            <MenuItem key={season.id} value={season.id}>
              {season.name}
            </MenuItem>
          ))}
        </Select>
        <Select
          size="small"
          displayEmpty
          value={countryFilter ?? ""}
          onChange={(event) => setCountryFilter(event.target.value || undefined)}
          disabled={leaguesLoading}
          sx={{ minWidth: { xs: "100%", md: 180 } }}
        >
          <MenuItem value="">All countries</MenuItem>
          {countryOptions.map((country) => (
            <MenuItem key={country} value={country}>
              {country}
            </MenuItem>
          ))}
        </Select>
        <TextField
          size="small"
          placeholder="Search league..."
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1 }}
        />
      </Stack>
    </Stack>
  );

  let tableContent: React.ReactNode;
  if (loading) {
    tableContent = (
      <Stack sx={{ alignItems: "center", py: 6 }}>
        <CircularProgress />
      </Stack>
    );
  } else if (error) {
    tableContent = <Alert severity="error">{error}</Alert>;
  } else if (!filteredChampionships.length) {
    tableContent = (
      <Alert severity="info">No championships match the current filters.</Alert>
    );
  } else {
    tableContent = (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>League</TableCell>
              <TableCell>Season</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Joined</TableCell>
              <TableCell align="right">Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredChampionships.map((championship) => {
              const joined = myChampionship?.id === championship.id;
              const statusChip = getStatusChipProps(championship.status);
              const isSelected = selectedChampionshipId === championship.id;
              return (
                <TableRow
                  key={championship.id}
                  hover
                  selected={isSelected}
                  onClick={() => setSelectedChampionshipId(championship.id)}
                  sx={(theme) => ({
                    cursor: "pointer",
                    backgroundColor: joined ? alpha(theme.palette.warning.main, 0.08) : undefined,
                    "&:hover": {
                      backgroundColor: joined
                        ? alpha(theme.palette.warning.main, 0.12)
                        : alpha(theme.palette.action.hover, 0.25),
                    },
                    "&.Mui-selected": {
                      backgroundColor: alpha(theme.palette.primary.main, 0.12),
                      "&:hover": {
                        backgroundColor: alpha(theme.palette.primary.main, 0.18),
                      },
                    },
                  })}
                >
                  <TableCell sx={{ py: 1 }}>
                    <Stack spacing={0.25}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        {joined && <StarIcon fontSize="small" color="warning" />}
                        <Typography variant="body2" fontWeight={600}>
                          {championship.name}
                        </Typography>
                      </Stack>
                      <Typography variant="caption" color="text.secondary">
                        {championship.league.country} · {championship.league.name}
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell sx={{ py: 1 }}>{championship.season.name}</TableCell>
                  <TableCell sx={{ py: 1 }}>
                    <Chip size="small" color={statusChip.color} label={statusChip.label} />
                  </TableCell>
                  <TableCell sx={{ py: 1 }}>
                    {joined ? (
                      <Chip
                        size="small"
                        icon={<StarIcon fontSize="inherit" />}
                        label="Joined"
                        color="warning"
                      />
                    ) : (
                      "-"
                    )}
                  </TableCell>
                  <TableCell align="right" sx={{ py: 1 }}>
                    <Chip
                      component={RouterLink}
                      to={`/championships/${championship.id}`}
                      label="View"
                      clickable
                      color="primary"
                      variant="outlined"
                      onClick={(event) => event.stopPropagation()}
                    />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  const detailPanel = (
    <Card
      sx={{
        height: "100%",
        position: { lg: "sticky" },
        top: { lg: 96 },
      }}
    >
      <CardContent sx={{ height: "100%" }}>
        {selectedChampionship ? (
          <Stack spacing={1.5} sx={{ height: "100%" }}>
            <Stack spacing={0.5}>
              <Typography variant="h6">{selectedChampionship.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedChampionship.league.country} · {selectedChampionship.league.name}
              </Typography>
            </Stack>

            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                size="small"
                color={getStatusChipProps(selectedChampionship.status).color}
                label={getStatusChipProps(selectedChampionship.status).label}
              />
              <Typography variant="caption" color="text.secondary">
                {selectedChampionship.start_date} – {selectedChampionship.end_date}
              </Typography>
            </Stack>

            <Stack spacing={0.5}>
              <Typography variant="subtitle2">Season</Typography>
              <Typography variant="body2">{selectedChampionship.season.name}</Typography>
            </Stack>
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">Teams</Typography>
              <Typography variant="body2">
                {selectedChampionship.league.max_teams ?? 16} clubs
              </Typography>
            </Stack>
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">Kick-off time</Typography>
              <Typography variant="body2">
                {selectedChampionship.match_time ?? "13:00 (default)"}
              </Typography>
            </Stack>
            <Box sx={{ flexGrow: 1 }} />
            <Stack spacing={1}>
              <Button
                component={RouterLink}
                to={`/championships/${selectedChampionship.id}`}
                variant="contained"
                size="medium"
              >
                {myChampionship?.id === selectedChampionship.id ? "Continue" : "Open championship"}
              </Button>
              {myChampionship?.id === selectedChampionship.id && (
                <Typography variant="caption" color="text.secondary">
                  You are currently participating in this league.
                </Typography>
              )}
            </Stack>
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Select a championship from the list to see details.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
  const mainContent = (
    <Grid container spacing={3}>
      <Grid item xs={12} lg={8}>
        <Card>{tableContent}</Card>
      </Grid>
      <Grid item xs={12} lg={4}>
        {detailPanel}
      </Grid>
    </Grid>
  );

  return (
    <PageShell
      hero={hero}
      top={
        <Stack spacing={3}>
          {myChampionshipSection}
          {filtersToolbar}
        </Stack>
      }
      main={mainContent}
    />
  );
}

function getStatusChipProps(
  status: ChampionshipSummary["status"],
): { label: string; color: "default" | "primary" | "success" | "warning" } {
  switch (status) {
    case "in_progress":
      return { label: "In progress", color: "primary" };
    case "finished":
      return { label: "Finished", color: "default" };
    case "pending":
    default:
      return { label: "Not started", color: "warning" };
  }
}











