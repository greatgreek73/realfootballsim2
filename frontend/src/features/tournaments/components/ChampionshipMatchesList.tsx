import { Button, Chip, Stack, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

import { ChampionshipMatchSummary } from "@/types/tournaments";

interface ChampionshipMatchesListProps {
  matches: ChampionshipMatchSummary[];
  showRound?: boolean;
}

export const MATCH_STATUS_LABELS: Record<string, string> = {
  scheduled: "Scheduled",
  in_progress: "In progress",
  finished: "Finished",
  cancelled: "Cancelled",
  postponed: "Postponed",
  expired: "Finished",
};

const statusColor: Record<string, "default" | "success" | "warning" | "error"> = {
  scheduled: "default",
  in_progress: "warning",
  finished: "success",
  cancelled: "error",
  postponed: "warning",
  expired: "success",
};

export function ChampionshipMatchesList({
  matches,
  showRound = true,
}: ChampionshipMatchesListProps) {
  if (matches.length === 0) {
    return <Typography variant="body2">No fixtures yet.</Typography>;
  }

  return (
    <Stack spacing={1.5}>
      {matches.map((match) => {
        const label = MATCH_STATUS_LABELS[match.status] ?? match.status;
        const chipColor = statusColor[match.status] ?? "default";
        return (
          <Stack
            key={match.id}
            direction={{ xs: "column", md: "row" }}
            spacing={2}
            alignItems={{ xs: "flex-start", md: "center" }}
            sx={{ py: 1.5, borderBottom: "1px solid", borderColor: "divider" }}
          >
            {showRound && (
              <Typography width={{ xs: "auto", md: 100 }} variant="body2" color="text.secondary">
                Тур {match.round}
              </Typography>
            )}
            <Stack flex={1} spacing={0.5}>
              <Typography variant="body1">
                {match.home_team.name} - {match.away_team.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {match.date}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                <Chip size="small" color={chipColor} label={label} />
                <Typography width={70} textAlign="right">
                  {match.score ? `${match.score.home}:${match.score.away}` : "-"}
                </Typography>
              </Stack>
            </Stack>
            <Button
              component={RouterLink}
              to={`/matches/${match.match_id}`}
              size="small"
              variant="outlined"
              sx={{ whiteSpace: "nowrap" }}
            >
              View
            </Button>
          </Stack>
        );
      })}
    </Stack>
  );
}
