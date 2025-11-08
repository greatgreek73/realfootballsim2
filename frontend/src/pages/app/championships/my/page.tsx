import { useMemo } from "react";

import { Link as RouterLink } from "react-router-dom";
import { Alert, Box, Button, Card, CardContent, Chip, CircularProgress, Stack, Typography } from "@mui/material";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import GroupsIcon from "@mui/icons-material/Groups";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import SportsSoccerIcon from "@mui/icons-material/SportsSoccer";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
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

  const nextMatch =
    schedule.find((match) => new Date(match.date).getTime() >= Date.now()) ?? (schedule.length > 0 ? schedule[0] : null);
  const nextMatchLabel = nextMatch ? `${nextMatch.home_team.name} vs ${nextMatch.away_team.name}` : "No fixtures";
  const nextMatchDate = nextMatch ? new Date(nextMatch.date).toLocaleString() : "TBD";
  const playedCount = Array.isArray(data.last_results) ? data.last_results.length : 0;
  const upcomingCount = Array.isArray(data.next_matches) ? data.next_matches.length : 0;

  const hero = (
    <HeroBar
      title={data.championship.name}
      subtitle={`${data.championship.league.name} · ${data.championship.season.name}`}
      tone="purple"
      kpis={[
        { label: "Position", value: data.club_position ?? "-", icon: <LeaderboardIcon fontSize="small" />, hint: "Current standing" },
        { label: "Teams", value: data.standings.length, icon: <GroupsIcon fontSize="small" />, hint: "Clubs in league" },
        { label: "Next game", value: nextMatchDate, icon: <EventAvailableIcon fontSize="small" />, hint: nextMatchLabel },
        { label: "Fixtures", value: schedule.length, icon: <SportsSoccerIcon fontSize="small" />, hint: "Season schedule" },
      ]}
      actions={
        <Button component={RouterLink} to={`/championships/${data.championship.id}`} size="small" variant="outlined">
          View details
        </Button>
      }
    />
  );



  const topSection = (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="subtitle1" fontWeight={600}>
            Match focus
          </Typography>
          <Stack direction={{ xs: "column", md: "row" }} spacing={1.5} flexWrap="wrap">
            <Chip label={`Played: ${playedCount}`} />
            <Chip label={`Upcoming: ${upcomingCount}`} />
            <Chip label={`Schedule size: ${schedule.length}`} />
            <Chip label={`Next: ${nextMatchLabel}`} color="secondary" />
          </Stack>
        </Stack>
      </CardContent>
    </Card>
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
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2, textAlign: { md: "right" } }}>
          Season schedule
        </Typography>
        {schedule.length === 0 ? (
          <Typography variant="body2">No fixtures available.</Typography>
        ) : (
          <ChampionshipMatchesList matches={schedule} />
        )}
      </CardContent>
    </Card>
  );
  return <PageShell hero={hero} top={topSection} main={mainContent} aside={asideContent} />;
}
