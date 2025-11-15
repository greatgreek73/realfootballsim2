import { Link as RouterLink } from "react-router-dom";

import { Alert, Button, Card, CardActions, CardContent, CardHeader, Skeleton, Stack, Typography } from "@mui/material";

import type { MatchSummary } from "@/api/matches";

export type ClubScheduleProps = {
  loading: boolean;
  matches: MatchSummary[];
  clubId?: number;
  error?: string | null;
};

function describeMatch(match: MatchSummary, clubId?: number) {
  const isHome = clubId ? match.home.id === clubId : true;
  const opponent = isHome ? match.away.name : match.home.name;
  const venue = isHome ? "Home" : "Away";
  return { opponent, venue };
}

function formatDate(value: string | null) {
  if (!value) return "TBD";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export default function ClubSchedule({ loading, matches, clubId, error }: ClubScheduleProps) {
  const fixtures = matches.slice(0, 4);

  return (
    <Card className="h-full">
      <CardHeader title="Upcoming Fixtures" subheader="Next matches on the calendar" />
      <CardContent>
        {error ? (
          <Alert severity="warning">{error}</Alert>
        ) : loading ? (
          <Stack spacing={2}>
            <Skeleton height={24} />
            <Skeleton height={24} />
            <Skeleton height={24} />
          </Stack>
        ) : fixtures.length ? (
          <Stack spacing={2}>
            {fixtures.map((fixture) => {
              const info = describeMatch(fixture, clubId);
              return (
                <Stack key={fixture.id} spacing={0.25}>
                  <Typography variant="body1">
                    {info.venue === "Home" ? "vs" : "@"} {info.opponent}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(fixture.datetime)} | {info.venue}
                  </Typography>
                </Stack>
              );
            })}
          </Stack>
        ) : (
          <Stack spacing={1}>
            <Typography variant="body2" color="text.secondary">
              No upcoming fixtures yet.
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Scheduled matches will appear here once the season calendar is released.
            </Typography>
          </Stack>
        )}
      </CardContent>
      <CardActions>
        <Button component={RouterLink} to="/matches" size="small">
          View all matches
        </Button>
      </CardActions>
    </Card>
  );
}
