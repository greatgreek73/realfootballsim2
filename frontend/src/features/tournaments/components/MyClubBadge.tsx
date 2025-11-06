import SportsSoccerIcon from "@mui/icons-material/SportsSoccer";
import { Chip } from "@mui/material";

interface MyClubBadgeProps {
  clubName: string;
  position?: number;
}

export function MyClubBadge({ clubName, position }: MyClubBadgeProps) {
  const label = position ? `${clubName} - position ${position}` : clubName;

  return (
    <Chip
      icon={<SportsSoccerIcon fontSize="small" />}
      color="primary"
      variant="outlined"
      label={label}
      size="small"
    />
  );
}
