import { Card, CardContent, Grid, List, ListItem, ListItemText, Typography } from "@mui/material";
import type { MatchDetail } from "@/api/matches";

const DATE_FORMATTER = new Intl.DateTimeFormat(undefined, {
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

function formatDate(value: string | null) {
  if (!value) return "TBD";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return DATE_FORMATTER.format(date);
}

export function StatsTimingGrid({ match }: { match: MatchDetail }) {
  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" className="mb-2">Statistics</Typography>
            <List dense>
              <ListItem>
                <ListItemText primary="Shots" secondary={`${match.stats.shoots ?? 0}`} />
              </ListItem>
              <ListItem>
                <ListItemText primary="Passes" secondary={`${match.stats.passes ?? 0}`} />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Possession"
                  secondary={`${match.stats.possessions ?? 0}%`}
                />
              </ListItem>
              <ListItem>
                <ListItemText primary="Fouls" secondary={`${match.stats.fouls ?? 0}`} />
              </ListItem>
              <ListItem>
                <ListItemText primary="Injuries" secondary={`${match.stats.injuries ?? 0}`} />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Momentum (home)"
                  secondary={`${match.stats.home_momentum ?? 0}`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Momentum (away)"
                  secondary={`${match.stats.away_momentum ?? 0}`}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" className="mb-2">Timing</Typography>
            <List dense>
              <ListItem><ListItemText primary="Match start" secondary={formatDate(match.started_at)} /></ListItem>
              <ListItem><ListItemText primary="Last update" secondary={formatDate(match.last_minute_update)} /></ListItem>
              <ListItem><ListItemText primary="Waiting for next minute" secondary={match.waiting_for_next_minute ? "Yes" : "No"} /></ListItem>
              <ListItem><ListItemText primary="Result processed" secondary={match.processed ? "Completed" : "Pending"} /></ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
