import { Avatar, Box, Button, Card, CardContent, ListItemIcon, MenuItem, MenuList, Tooltip, Typography } from "@mui/material";
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
  /** URL аватара игрока (если нет — будет показан плейсхолдер) */
  avatarUrl?: string; // ← добавлено
};

export default function PlayerProfileMenu({
  selected = "overview",
  playerId,
  playerName,
  avatarUrl, // ← добавлено
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
        <Box className="flex flex-row items-center gap-3 mb-2">
          <Avatar src={avatarUrl ?? "/img/avatar-2.jpg"} sx={{ width: 40, height: 40 }}>
            {initials(playerName)}
          </Avatar>
          <Typography variant="subtitle1" title={playerName ?? "Player"}>
            {playerName ?? "Player"}
          </Typography>
          <Tooltip title="Actions">
            <Button className="icon-only ml-auto" size="medium" color="primary" variant="pastel">
              <NiEllipsisHorizontal size={"medium"} />
            </Button>
          </Tooltip>
        </Box>

        <Box className="w-full">
          <MenuList className="p-0">
            <MenuItem selected={selected === "overview"} onClick={() => go("/player/overview")} disabled={!playerId}>
              <ListItemIcon><NiPulse size={20} /></ListItemIcon>
              Overview
            </MenuItem>
            <MenuItem selected={selected === "training"} onClick={() => go("/player/overview")} disabled>
              <ListItemIcon><NiFolder size={20} /></ListItemIcon>
              Training
            </MenuItem>
            <MenuItem selected={selected === "history"} onClick={() => go("/player/overview")} disabled>
              <ListItemIcon><NiLock size={20} /></ListItemIcon>
              History
            </MenuItem>
            <MenuItem selected={selected === "social"} onClick={() => go("/player/overview")} disabled>
              <ListItemIcon><NiController size={20} /></ListItemIcon>
              Social
            </MenuItem>
          </MenuList>
        </Box>
      </CardContent>
    </Card>
  );
}
