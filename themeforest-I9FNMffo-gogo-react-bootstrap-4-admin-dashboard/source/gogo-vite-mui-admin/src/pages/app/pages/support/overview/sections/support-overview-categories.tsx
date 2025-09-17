import { useNavigate } from "react-router-dom";

import {
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";

import NiDashboard from "@/icons/nexture/ni-dashboard";
import NiDevops from "@/icons/nexture/ni-devops";
import NiScreen from "@/icons/nexture/ni-screen";
import NiServer from "@/icons/nexture/ni-server";
import NiShield from "@/icons/nexture/ni-shield";
import NiShuffle from "@/icons/nexture/ni-shuffle";

export default function SupportOverviewCategories() {
  const navigate = useNavigate();

  const handleCategoryClick = (event: any) => {
    event.preventDefault();
    navigate("/pages/support/issues");
  };

  return (
    <>
      <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
        Categories
      </Typography>
      <CardContent className="px-2! pt-0! pb-2!">
        <List dense>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemIcon>
                <NiDashboard className="text-primary" size="medium" />
              </ListItemIcon>
              <ListItemText primary="Performance" />
              <Chip label="68" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Slow loading times" className="pl-[1.75rem]" />
              <Chip label="24" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Server response delays" className="pl-[1.75rem]" />
              <Chip label="14" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="High memory or CPU usage" className="pl-[1.75rem]" />
              <Chip label="14" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Asset delivery delays" className="pl-[1.75rem]" />
              <Chip label="14" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <Divider className="border-none" />

          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemIcon>
                <NiShield className="text-secondary" size="medium" />
              </ListItemIcon>
              <ListItemText primary="Security" />
              <Chip label="71" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Unauthorized data access" className="pl-[1.75rem]" />
              <Chip label="10" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Cross-site scripting" className="pl-[1.75rem]" />
              <Chip label="26" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="SQL injection" className="pl-[1.75rem]" />
              <Chip label="13" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Weak password enforcement" className="pl-[1.75rem]" />
              <Chip label="16" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <Divider className="border-none" />

          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemIcon>
                <NiScreen className="text-accent-1" size="medium" />
              </ListItemIcon>
              <ListItemText primary="Interface" />
              <Chip label="24" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Inconsistent design" className="pl-[1.75rem]" />
              <Chip label="6" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Navigation difficulties" className="pl-[1.75rem]" />
              <Chip label="8" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Accessibility concerns" className="pl-[1.75rem]" />
              <Chip label="5" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Confusing error messages" className="pl-[1.75rem]" />
              <Chip label="4" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <Divider className="border-none" />

          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemIcon>
                <NiShuffle className="text-accent-2" size="medium" />
              </ListItemIcon>
              <ListItemText primary="Functional" />
              <Chip label="8" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Broken links" className="pl-[1.75rem]" />
              <Chip label="5" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Forms not submitting correctly" className="pl-[1.75rem]" />
              <Chip label="3" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <Divider className="border-none" />

          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemIcon>
                <NiDevops className="text-accent-3" size="medium" />
              </ListItemIcon>
              <ListItemText primary="Compatibility" />
              <Chip label="36" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Browser compatibility issues" className="pl-[1.75rem]" />
              <Chip label="6" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Mobile responsiveness" className="pl-[1.75rem]" />
              <Chip label="8" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="OS-specific bugs" className="pl-[1.75rem]" />
              <Chip label="9" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>

          <Divider className="border-none" />

          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemIcon>
                <NiServer className="text-accent-4" size="medium" />
              </ListItemIcon>
              <ListItemText primary="Database" />
              <Chip label="48" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Database connection failures" className="pl-[1.75rem]" />
              <Chip label="6" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Data storage bottlenecks" className="pl-[1.75rem]" />
              <Chip label="8" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Inadequate error handling" className="pl-[1.75rem]" />
              <Chip label="9" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={handleCategoryClick}>
              <ListItemText primary="Failure in data migration" className="pl-[1.75rem]" />
              <Chip label="4" variant="filled" className="text-sm" />
            </ListItemButton>
          </ListItem>
        </List>
      </CardContent>
    </>
  );
}
