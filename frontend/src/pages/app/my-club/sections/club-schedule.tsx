import { Link as RouterLink } from "react-router-dom";

import { Alert, Button, Card, CardActions, CardContent, CardHeader, Skeleton, Stack, Typography } from "@mui/material";

export type ClubFixture = {
  id: string | number;
  opponent: string;
  date: string;
  venue?: string;
};

export type ClubScheduleProps = {
  loading: boolean;
  fixtures?: ClubFixture[];
  error?: string | null;
};

export default function ClubSchedule({ loading, fixtures = [], error }: ClubScheduleProps) {
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
            {fixtures.map((fixture) => (
              <Stack key={fixture.id} spacing={0.25}>
                <Typography variant="body1">{fixture.opponent}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {fixture.date}
                  {fixture.venue ? ` | ${fixture.venue}` : ""}
                </Typography>
              </Stack>
            ))}
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
