import { Link as RouterLink } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Skeleton,
  Stack,
  Typography,
} from "@mui/material";

import type { MatchSummary } from "@/api/matches";

type ClubNextMatchProps = {
  match: MatchSummary | null;
  loading: boolean;
  clubId?: number;
};

function formatDateTime(value: string | null) {
  if (!value) {
    return "Date TBD";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export default function ClubNextMatch({ match, loading, clubId }: ClubNextMatchProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader title="Next match" subheader="Upcoming opponent overview" />
        <CardContent>
          <Skeleton variant="text" height={32} width="60%" />
          <Skeleton variant="text" height={24} width="40%" />
          <Skeleton variant="rectangular" height={48} />
        </CardContent>
      </Card>
    );
  }

  if (!match) {
    return (
      <Card>
        <CardHeader title="Next match" subheader="Upcoming opponent overview" />
        <CardContent>
          <Alert severity="info">No upcoming fixtures scheduled yet.</Alert>
        </CardContent>
      </Card>
    );
  }

  const isHome = clubId != null ? match.home.id === clubId : true;
  const opponent = isHome ? match.away.name : match.home.name;
  const venueLabel = isHome ? "Home" : "Away";

  return (
    <Card>
      <CardHeader title="Next match" subheader="Stay ready for the next kick-off" />
      <CardContent>
        <Stack spacing={2}>
          <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={1}>
            <Typography variant="h5" component="div">
              {opponent}
            </Typography>
            <Chip
              label={`${venueLabel} · ${match.status_label}`}
              color={match.status === "finished" ? "default" : "primary"}
              variant="outlined"
              size="small"
            />
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {formatDateTime(match.datetime)}
          </Typography>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Fixture difficulty
            </Typography>
            <Typography variant="body2">Insights coming soon</Typography>
          </Box>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Button
              component={RouterLink}
              to={`/matches/${match.id}`}
              variant="contained"
              size="medium"
              fullWidth
            >
              Open match
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}

