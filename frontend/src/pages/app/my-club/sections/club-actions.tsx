import { Box, Button, Card, CardContent, Stack, Tooltip } from "@mui/material";
import type { CardProps } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

export type ClubActionsProps = {
  club: {
    id: number;
  } | null;
  loading: boolean;
  nextMatchId?: number | null;
  cardProps?: CardProps;
};

export default function ClubActions({ club, loading, nextMatchId, cardProps }: ClubActionsProps) {
  const disabled = loading || !club;

  return (
    <Card className="h-full" {...cardProps}>
      <CardContent
        sx={{
          height: "100%",
          width: "100%",
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Stack spacing={1.5} sx={{ width: "100%", maxWidth: 380, mx: "auto" }} alignItems="stretch">
          <Tooltip title={disabled ? "Not available yet" : "Open lineup selection"} placement="top-start">
            <Box component="span" sx={{ display: "block", width: "100%" }}>
              <Button variant="contained" size="medium" fullWidth disabled={disabled}>
                Select Team Lineup
              </Button>
            </Box>
          </Tooltip>
          <Tooltip title={nextMatchId ? "Jump to the upcoming match" : "No upcoming match available"} placement="top-start">
            <Box component="span" sx={{ display: "block", width: "100%" }}>
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
            </Box>
          </Tooltip>
          <Tooltip title="Feature in development" placement="top-start">
            <Box component="span" sx={{ display: "block", width: "100%" }}>
              <Button variant="outlined" size="medium" fullWidth disabled>
                Training (soon)
              </Button>
            </Box>
          </Tooltip>
          <Button component={RouterLink} to="/transfers" variant="outlined" size="medium" fullWidth disabled={disabled}>
            Transfer Market
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
