import UserAchievements from "../sections/user-achievements";
import UserProfileMenu from "../sections/user-profile-menu";
import UserSpecialties from "../sections/user-specialties";
import UserPermissionsList from "./sections/user-permissions-list";
import { SyntheticEvent, useState } from "react";
import { Link } from "react-router-dom";

import {
  Breadcrumbs,
  Button,
  Fade,
  Grid,
  Menu,
  MenuItem,
  PopoverVirtualElement,
  Tooltip,
  Typography,
} from "@mui/material";

import NiEllipsisHorizontal from "@/template_full/icons/nexture/ni-ellipsis-horizontal";

export default function Page() {
  const [anchorElMainMenu, setAnchorElMainMenu] = useState<EventTarget | Element | PopoverVirtualElement | null>(null);
  const open = Boolean(anchorElMainMenu);
  const handleClickMainMenu = (event: Event | SyntheticEvent) => {
    setAnchorElMainMenu(event.currentTarget);
  };
  const handleCloseMainMenu = () => {
    setAnchorElMainMenu(null);
  };

  return (
    <Grid container spacing={5} className="w-full" size={12}>
      <Grid container spacing={2.5} className="w-full" size={12}>
        <Grid size={{ md: "grow", xs: 12 }}>
          <Typography variant="h1" component="h1" className="mb-0">
            Laura Ellis
          </Typography>
          <Breadcrumbs>
            <Link color="inherit" to="/dashboards/default">
              Home
            </Link>
            <Link color="inherit" to="/pages">
              Pages
            </Link>
            <Link color="inherit" to="/pages/user">
              User
            </Link>
            <Typography variant="body2">Laura Ellis</Typography>
          </Breadcrumbs>
        </Grid>

        <Grid size={{ xs: 12, md: "auto" }} className="flex flex-row items-start gap-2">
          <Tooltip title="Actions">
            <Button className="icon-only surface-standard" color="grey" variant="surface" onClick={handleClickMainMenu}>
              <NiEllipsisHorizontal size={"medium"} />
            </Button>
          </Tooltip>

          <Menu
            anchorEl={anchorElMainMenu as Element}
            open={open}
            onClose={handleCloseMainMenu}
            className="mt-1"
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "right",
            }}
            transformOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
            slots={{
              transition: Fade,
            }}
          >
            <MenuItem>Contact</MenuItem>
            <MenuItem>Follow</MenuItem>
            <MenuItem>Mute</MenuItem>
            <MenuItem>Report</MenuItem>
          </Menu>
        </Grid>
      </Grid>
      <Grid container size={12}>
        <Grid size={{ "3xl": 3, lg: 4, xs: 12 }}>
          <UserProfileMenu selected="permissions" />
          <UserAchievements />
          <UserSpecialties />
        </Grid>

        <Grid container size={{ "3xl": 9, lg: 8, xs: 12 }}>
          <UserPermissionsList />
        </Grid>
      </Grid>
    </Grid>
  );
}

