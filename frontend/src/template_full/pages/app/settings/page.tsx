import SettingsContact from "./examples/settings-contact";
import SettingsPublicInfo from "./examples/settings-public-info";
import SettingsWork from "./examples/settings-work";
import { useState } from "react";
import { Link } from "react-router-dom";

import {
  Box,
  Breadcrumbs,
  Button,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Typography,
} from "@mui/material";
import { Grid } from "@mui/material";

import NiBasket from "@/template_full/icons/nexture/ni-basket";
import NiBell from "@/template_full/icons/nexture/ni-bell";
import NiCheckSquare from "@/template_full/icons/nexture/ni-check-square";
import NiDocumentFull from "@/template_full/icons/nexture/ni-document-full";
import NiEmail from "@/template_full/icons/nexture/ni-email";
import NiLaptop from "@/template_full/icons/nexture/ni-laptop";
import NiListCircle from "@/template_full/icons/nexture/ni-list-circle";
import NiLock from "@/template_full/icons/nexture/ni-lock";
import NiMoneyBag from "@/template_full/icons/nexture/ni-money-bag";
import NiPaintRoller from "@/template_full/icons/nexture/ni-paint-roller";
import NiReceipt from "@/template_full/icons/nexture/ni-receipt";
import NiStars from "@/template_full/icons/nexture/ni-stars";
import NiUser from "@/template_full/icons/nexture/ni-user";
import NiUsers from "@/template_full/icons/nexture/ni-users";
import NiWallet from "@/template_full/icons/nexture/ni-wallet";

const MenuContent = () => {
  return (
    <Box className="flex flex-col gap-4">
      <List className="-mt-6">
        <ListItem disablePadding>
          <ListItemButton className="pointer-events-none mt-4">
            <ListItemText
              primary="Personal"
              slotProps={{
                primary: { className: "text-xs! font-semibold! opacity-40" },
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link} selected>
            <ListItemIcon>
              <NiUser size="medium" />
            </ListItemIcon>
            <ListItemText primary="Profile" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiUsers size="medium" />
            </ListItemIcon>
            <ListItemText primary="Friends" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiDocumentFull size="medium" />
            </ListItemIcon>
            <ListItemText primary="Account" />
          </ListItemButton>
        </ListItem>

        <ListItem disablePadding>
          <ListItemButton className="pointer-events-none mt-4">
            <ListItemText
              primary="Payment"
              slotProps={{
                primary: { className: "text-xs! font-semibold! opacity-40" },
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiWallet size="medium" />
            </ListItemIcon>
            <ListItemText primary="Billing" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiReceipt size="medium" />
            </ListItemIcon>
            <ListItemText primary="Invoice" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiMoneyBag size="medium" />
            </ListItemIcon>
            <ListItemText primary="Tax Info" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiBasket size="medium" />
            </ListItemIcon>
            <ListItemText primary="Payment Methods" />
          </ListItemButton>
        </ListItem>

        <ListItem disablePadding>
          <ListItemButton className="pointer-events-none mt-4">
            <ListItemText
              primary="Security"
              slotProps={{
                primary: { className: "text-xs! font-semibold! opacity-40" },
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiLock size="medium" />
            </ListItemIcon>
            <ListItemText primary="Password" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiCheckSquare size="medium" />
            </ListItemIcon>
            <ListItemText primary="Two Factor Auth" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiLaptop size="medium" />
            </ListItemIcon>
            <ListItemText primary="Devices" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiListCircle size="medium" />
            </ListItemIcon>
            <ListItemText primary="Logs" />
          </ListItemButton>
        </ListItem>

        <ListItem disablePadding>
          <ListItemButton className="pointer-events-none mt-4">
            <ListItemText
              primary="Preferences"
              slotProps={{
                primary: { className: "text-xs! font-semibold! opacity-40" },
              }}
            />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiBell size="medium" />
            </ListItemIcon>
            <ListItemText primary="Notifications" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiEmail size="medium" />
            </ListItemIcon>
            <ListItemText primary="Emails" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiPaintRoller size="medium" />
            </ListItemIcon>
            <ListItemText primary="Appearance" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton href="/settings" LinkComponent={Link}>
            <ListItemIcon>
              <NiStars size="medium" />
            </ListItemIcon>
            <ListItemText primary="Moderation" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );
};

export default function Settings() {
  const [openDrawer, setOpenDrawer] = useState(false);

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpenDrawer(newOpen);
  };

  return (
    <Grid container spacing={5} className="items-start">
      <Grid size={"auto"} className="hidden pr-8 lg:flex">
        <MenuContent />
      </Grid>
      <Grid size={"grow"} spacing={5} container>
        <Grid size={12} spacing={2.5} container>
          <Grid size={{ xs: 12, md: "grow" }}>
            <Typography variant="h1" component="h1" className="mb-0">
              Profile
            </Typography>
            <Breadcrumbs>
              <Link color="inherit" to="/dashboards/default">
                Home
              </Link>
              <Link color="inherit" to="/settings">
                Settings
              </Link>
              <Typography variant="body2">Profile</Typography>
            </Breadcrumbs>
          </Grid>
          <Grid size={{ xs: 12, md: "auto" }} className="lg:hidden">
            <Tooltip title="Table of Contents">
              <Button
                className="icon-only surface-standard"
                color="grey"
                variant="surface"
                onClick={toggleDrawer(true)}
              >
                <NiListCircle size={"medium"} />
              </Button>
            </Tooltip>
          </Grid>
        </Grid>

        <SettingsPublicInfo />
        <SettingsContact />
        <SettingsWork />

        <Drawer open={openDrawer} anchor="right" onClose={toggleDrawer(false)}>
          <Box className="min-w-80 p-7">
            <MenuContent />
          </Box>
        </Drawer>
      </Grid>
    </Grid>
  );
}

