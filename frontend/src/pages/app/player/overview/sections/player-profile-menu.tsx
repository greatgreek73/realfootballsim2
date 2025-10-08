import { Avatar, Box, Button, Card, CardContent, CircularProgress, ListItemIcon, MenuItem, MenuList, Tooltip, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

import NiPulse from "@/icons/nexture/ni-pulse";
import NiFolder from "@/icons/nexture/ni-folder";
import NiLock from "@/icons/nexture/ni-lock";
import NiController from "@/icons/nexture/ni-controller";
import NiEllipsisHorizontal from "@/icons/nexture/ni-ellipsis-horizontal";

type PlayerProfileMenuProps = {
  selected?: "overview" | "training" | "history" | "social";
  playerId?: string | number;
  playerName?: string;
  avatarUrl?: string;
  onTraining?: () => void;
  trainingDisabled?: boolean;
  trainingLoading?: boolean;
};

const AVATAR_DESKTOP = 480;

export default function PlayerProfileMenu({
  selected = "overview",
  playerId,
  playerName,
  avatarUrl,
  onTraining,
  trainingDisabled,
  trainingLoading,
}: PlayerProfileMenuProps) {
  const navigate = useNavigate();
  const go = (path: string) => {
    if (!playerId) return;
    navigate(`${path}?id=${playerId}`);
  };

  const initials = (name?: string) => {
    if (!name) return "P";
    const parts = name.split(" ").filter(Boolean);
    return ((parts[0]?.[0] ?? "") + (parts[1]?.[0] ?? "")).toUpperCase() || "P";
  };

  return (
    <Card className="mb-2.5">
      <CardContent>
        <Box className="flex flex-col items-center text-center mb-2">
          <Avatar
            src={avatarUrl ?? "/img/avatar-2.jpg"}
            sx={{
              width: { xs: 128, sm: 192, md: 240, lg: 320, xl: AVATAR_DESKTOP },
              height: { xs: 128, sm: 192, md: 240, lg: 320, xl: AVATAR_DESKTOP },
              mb: 1.5,
            }}
            style={{
              width: "min(160px, 60vh, 100%)",
              height: "min(160px, 60vh, 100%)",
            }}
          >
            {initials(playerName)}
          </Avatar>

          <Typography variant="h6" className="mb-0 truncate" title={playerName ?? "Player"}>
            {playerName ?? "Player"}
          </Typography>

          <Typography variant="body2" className="text-text-secondary mb-2">
            Lorem ipsum dolor
          </Typography>

          <Box className="flex flex-row items-center justify-center gap-1.5">
            <Button
              size="medium"
              color="primary"
              variant="contained"
              disableElevation
              startIcon={<NiPulse size={20} />}
            >
              Contact
            </Button>
            <Button size="medium" color="primary" variant="pastel">
              Follow
            </Button>
            <Tooltip title="Actions">
              <Button className="icon-only" size="medium" color="primary" variant="pastel">
                <NiEllipsisHorizontal size={"medium"} />
              </Button>
            </Tooltip>
          </Box>
        </Box>

        <Box className="w-full">
          <MenuList className="p-0">
            <MenuItem selected={selected === "overview"} onClick={() => go("/player/overview")} disabled={!playerId}>
              <ListItemIcon>
                <NiPulse size={20} />
              </ListItemIcon>
              Overview
            </MenuItem>
            <MenuItem
              selected={selected === "training"}
              onClick={() => {
                if (trainingDisabled || !playerId) return;
                if (onTraining) {
                  onTraining();
                } else {
                  go("/player/overview");
                }
              }}
              disabled={trainingDisabled || !playerId}
              className="flex items-center justify-between"
            >
              <ListItemIcon>
                <NiFolder size={20} />
              </ListItemIcon>
              <Box component="span" className="flex-1">
                Training
              </Box>
              {trainingLoading && <CircularProgress size={16} />}
            </MenuItem>
            <MenuItem selected={selected === "history"} onClick={() => go("/player/overview")} disabled>
              <ListItemIcon>
                <NiLock size={20} />
              </ListItemIcon>
              History
            </MenuItem>
            <MenuItem selected={selected === "social"} onClick={() => go("/player/overview")} disabled>
              <ListItemIcon>
                <NiController size={20} />
              </ListItemIcon>
              Social
            </MenuItem>
          </MenuList>
        </Box>
      </CardContent>
    </Card>
  );
}
