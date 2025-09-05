import {
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";

import NiCake from "@/template_full/icons/nexture/ni-cake";
import NiEmail from "@/template_full/icons/nexture/ni-email";
import NiEyeOpen from "@/template_full/icons/nexture/ni-eye-open";
import NiRocket from "@/template_full/icons/nexture/ni-rocket";
import NiUser from "@/template_full/icons/nexture/ni-user";
import NiUsers from "@/template_full/icons/nexture/ni-users";
import NiWallet from "@/template_full/icons/nexture/ni-wallet";

export default function FaqCategories() {
  return (
    <>
      <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
        Categories
      </Typography>
      <CardContent className="px-2! pt-0! pb-2!">
        <List>
          <ListItem disablePadding>
            <ListItemButton selected>
              <ListItemIcon>
                <NiRocket size="medium" />
              </ListItemIcon>
              <ListItemText primary="Getting Started" />
              <Chip label="5" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <NiUser size="medium" />
              </ListItemIcon>
              <ListItemText primary="Account Management" />
              <Chip label="3" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <NiCake size="medium" />
              </ListItemIcon>
              <ListItemText primary="Features & Functionality" />
              <Chip label="6" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <NiWallet size="medium" />
              </ListItemIcon>
              <ListItemText primary="Billing & Payments" />
              <Chip label="3" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <NiEyeOpen size="medium" />
              </ListItemIcon>
              <ListItemText primary="Privacy & Security" />
              <Chip label="6" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <NiUsers size="medium" />
              </ListItemIcon>
              <ListItemText primary="Community Guidelines" />
              <Chip label="2" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <NiEmail size="medium" />
              </ListItemIcon>
              <ListItemText primary="Contact & Support" />
              <Chip label="3" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
        </List>
      </CardContent>
    </>
  );
}

