import { Button, Card, CardContent, Stack, Tooltip } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

export type ClubActionsProps = {
  club: {
    id: number;
  } | null;
  loading: boolean;
  nextMatchId?: number | null;
};

export default function ClubActions({ club, loading, nextMatchId }: ClubActionsProps) {
  const disabled = loading || !club;

  return (
    <Card className="h-full">
      <CardContent>
        <Stack spacing={1.5}>
          <Tooltip title={disabled ? "Not available yet" : "Open lineup selection"} placement="top-start">
            <span>
              <Button variant="contained" size="medium" fullWidth disabled={disabled}>
                Select Team Lineup
              </Button>
            </span>
          </Tooltip>
          <Tooltip title={nextMatchId ? "Jump to the upcoming match" : "No upcoming match available"} placement="top-start">
            <span>
              <Button
                component={RouterLink}
                to={nextMatchId ? `/matches/${nextMatchId}` : "#"}
                variant="outlined"
                size="medium"
                fullWidth
                disabled={!nextMatchId}
              >
                Open next match
              </Button>
            </span>
          </Tooltip>
          <Tooltip title="Feature in development" placement="top-start">
            <span>
              <Button variant="outlined" size="medium" fullWidth disabled>
                Training (soon)
              </Button>
            </span>
          </Tooltip>
          <Button component={RouterLink} to="/transfers" variant="outlined" size="medium" fullWidth disabled={disabled}>
            Transfer Market
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
