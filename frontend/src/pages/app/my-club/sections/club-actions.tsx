import { Button, Card, CardContent, Stack, Tooltip } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

export type ClubActionsProps = {
  club: {
    id: number;
  } | null;
  loading: boolean;
};

export default function ClubActions({ club, loading }: ClubActionsProps) {
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
