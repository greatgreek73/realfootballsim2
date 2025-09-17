import { useNavigate } from "react-router-dom";

import {
  Button,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import Box from "@mui/material/Box";

import NiCalendar from "@/icons/nexture/ni-calendar";
import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";
import NiDevops from "@/icons/nexture/ni-devops";
import NiDocumentFull from "@/icons/nexture/ni-document-full";
import NiFire from "@/icons/nexture/ni-fire";
import NiFlask from "@/icons/nexture/ni-flask";
import NiIntegration from "@/icons/nexture/ni-integration";
import NiQuestionHexagon from "@/icons/nexture/ni-question-hexagon";
import NiScreen from "@/icons/nexture/ni-screen";
import NiSendUpRight from "@/icons/nexture/ni-send-up-right";
import NiSettings from "@/icons/nexture/ni-settings";
import NiShieldCheck from "@/icons/nexture/ni-shield-check";
import NiStars from "@/icons/nexture/ni-stars";

export default function KnowledgeBaseReference() {
  const navigate = useNavigate();

  const handleCategoryClick = (event: any) => {
    event.preventDefault();
    navigate("/pages/miscellaneous/article");
  };

  return (
    <Card className="h-full">
      <CardContent>
        <Box className="mb-3 flex flex-row items-center leading-6">
          <Typography variant="h5" component="h5" className="flex-1">
            Reference
          </Typography>
          <Button size="tiny" color="grey" variant="text" startIcon={<NiChevronRightSmall size={"tiny"} />}>
            Get Started
          </Button>
        </Box>

        <Grid container size={12} spacing={5}>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiFire className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Introduction to the Application" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Features Overview" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Target Audience" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Benefits of Using the Application" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Frequently Used Terms" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Application Architecture" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiSendUpRight className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Getting Started Guide" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Installation Instructions" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="First-Time User Tips" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Quick Start Checklist" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Understanding Key Features" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Setting Up Notifications" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiSettings className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="System Requirements" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Hardware Specifications" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Software Compatibility" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Supported Languages" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Supported Browser Versions" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiScreen className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="User Interface Overview" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Icon Glossary" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Navigation Menus" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Accessibility Features" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Keyboard Shortcuts" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiFlask className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Core Features and Functions" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Advanced Tools Guide" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Collaboration Features" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Offline Mode" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Importing and Exporting Data" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Scheduling and Automation" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiDocumentFull className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="API Reference Documentation" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Pagination and Filtering" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Webhooks and Events" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Rate Limiting Details" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiShieldCheck className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Authentication and Security" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Two-Factor Authentication Setup" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Password Recovery Guide" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Privacy Policies" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Access Token Expiry" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiDevops className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Data Models and Schemas" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Attribute Definitions" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Sample Queries" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Data Export Methods" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Field-Level Constraints" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiQuestionHexagon className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Troubleshooting and FAQs" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Network Connection Issues" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Error Code Interpretations" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Contact Support Options" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Browser Cache Issues" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Resolving Account Lockouts" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiCalendar className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Version History and Updates" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Deprecated Features" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Bug Fixes Log" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Upcoming Releases" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Major vs. Minor Updates" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiIntegration className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Integrations and Plugins" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="API Integration Tutorials" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Plugin Marketplace" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Troubleshooting Integration Issues" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
          <Grid container size={{ "3xl": 3, "2xl": 4, lg: 6, xs: 12 }}>
            <List className="w-full">
              <ListItem disablePadding>
                <ListItemButton className="pointer-events-none">
                  <ListItemIcon>
                    <NiStars className="text-primary" size="medium" />
                  </ListItemIcon>
                  <ListItemText primary="Best Practices and Tips" className="text-primary" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Workflow Optimization" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton onClick={handleCategoryClick}>
                  <ListItemText primary="Time-Saving Hacks" className="pl-[1.75rem]" />
                </ListItemButton>
              </ListItem>
            </List>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
