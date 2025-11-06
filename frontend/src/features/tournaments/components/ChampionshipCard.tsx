import {
  Button,
  Card,
  CardActionArea,
  CardActions,
  CardContent,
  Chip,
  Stack,
  Typography,
} from "@mui/material";
import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { ChampionshipSummary } from "@/types/tournaments";

interface ChampionshipCardProps {
  championship: ChampionshipSummary;
  showNavigateAction?: boolean;
  onClick?: (championship: ChampionshipSummary) => void;
}

const statusLabels: Record<string, string> = {
  pending: "Not started",
  in_progress: "In progress",
  finished: "Finished",
};

export function ChampionshipCard({
  championship,
  showNavigateAction = true,
  onClick,
}: ChampionshipCardProps) {
  const navigate = useNavigate();

  const handleClick = useCallback(() => {
    if (onClick) {
      onClick(championship);
    } else if (showNavigateAction) {
      navigate(`/championships/${championship.id}`);
    }
  }, [championship, navigate, onClick, showNavigateAction]);

  const cardInner = (
    <CardContent sx={{ height: "100%" }}>
      <Stack spacing={0.75}>
        <Typography variant="h6">{championship.name}</Typography>
        <Typography variant="body2" color="text.secondary">
          {championship.league.country} - {championship.league.name}
        </Typography>
        <Typography variant="body2">{championship.season.name}</Typography>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
          <Chip
            size="small"
            label={statusLabels[championship.status] ?? championship.status}
            color={championship.status === "finished" ? "default" : "primary"}
          />
          <Typography variant="caption" color="text.secondary">
            {championship.start_date} - {championship.end_date}
          </Typography>
        </Stack>
      </Stack>
    </CardContent>
  );

  if (showNavigateAction || onClick) {
    return (
      <Card sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
        <CardActionArea onClick={handleClick} sx={{ flexGrow: 1 }}>
          {cardInner}
        </CardActionArea>
        {showNavigateAction && (
          <CardActions sx={{ justifyContent: "flex-end", pt: 0 }}>
            <Button size="small" onClick={handleClick}>
              Details
            </Button>
          </CardActions>
        )}
      </Card>
    );
  }

  return <Card>{cardInner}</Card>;
}
