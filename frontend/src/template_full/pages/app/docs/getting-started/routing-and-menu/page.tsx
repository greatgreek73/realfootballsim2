import DocsMenu from "../../sections/docs-menu";
import { useState } from "react";
import { Link } from "react-router-dom";
import SyntaxHighlighter from "react-syntax-highlighter";
import { atomOneDark, atomOneLight } from "react-syntax-highlighter/dist/esm/styles/hljs";

import { Box, Breadcrumbs, Button, Card, CardContent, Drawer, Tooltip, Typography } from "@mui/material";
import { Grid } from "@mui/material";

import NiListCircle from "@/icons/nexture/ni-list-circle";
import { useThemeContext } from "@/theme/theme-provider";

const MenuContent = () => {
  return (
    <Box className="flex flex-col gap-4">
      <DocsMenu selectedID="docs-routing-and-menu" />
    </Box>
  );
};

export default function DocsGettingStartedRoutingAndMenu() {
  const [openDrawer, setOpenDrawer] = useState(false);

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpenDrawer(newOpen);
  };

  const { isDarkMode } = useThemeContext();

  return (
    <Grid container spacing={5} className="items-start">
      <Grid size={"auto"} className="hidden pr-8 lg:flex">
        <MenuContent />
      </Grid>
      <Grid size={"grow"} spacing={5} container>
        <Grid size={12} spacing={2.5} container>
          <Grid size={{ xs: 12, md: "grow" }}>
            <Typography variant="h1" component="h1" className="mb-0">
              Routing and Menu
            </Typography>
            <Breadcrumbs>
              <Link color="inherit" to="/dashboards/default">
                Home
              </Link>
              <Link color="inherit" to="/docs">
                Docs
              </Link>
              <Link color="inherit" to="/docs/getting-started">
                Getting Started
              </Link>
              <Typography variant="body2">Routing and Menu</Typography>
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

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Menu Source
              </Typography>
              <Typography variant="body1" component="p">
                The menu works connected with the layout and you can find the source codes in{" "}
                <code>src/components/layout/menu</code> folder.
              </Typography>
              <Box className="bg-grey-20 syntax-highlighter mt-3 rounded-lg p-4">
                <SyntaxHighlighter
                  className="bg-transparent!"
                  language="asciidoc"
                  style={isDarkMode ? atomOneDark : atomOneLight}
                  codeTagProps={{ className: "border-none" }}
                  showLineNumbers
                >
                  {`+-- components
    | 
    +-- charts
    +-- data-grid
    +-- layout
    |   |
    |   +-- containers
    |   +-- menu                                       // Menu source codes
    |   |   |
    |   |   |-- left-menu.tsx                          // Left primary and secondary source
    |   |   |-- menu-backdrop.tsx                      // Custom click away area of the menu
    |   |   |-- primary-item.tsx                       // Primary menu item
    |   |   |-- secondary-item.tsx                     // Secondary menu item
    |   |   |
    |   +-- notifications
    |   +-- search
    |   +-- shortcuts
    |   +-- user
    |   |-- layout-context.tsx
    |   |-- listing-page-content.tsx
    +-- logo
    +-- plugins`}
                </SyntaxHighlighter>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Left Menu
              </Typography>
              <Typography variant="body1" component="p" className="mb-2">
                The left menu gets a list of menu items and navigates to them. The menu items can contain hrefs, labels,
                and icons. If there is a children array, the menu displays an accordion on the secondary panel. The menu
                data file is located in <code>src/menu-items.ts</code>. It has two arrays and they provide the data for
                the top and bottom left menu contents.
              </Typography>

              <Typography variant="body1" component="p">
                The routes are auto-generated from the <code>leftMenuItems</code> and <code>leftMenuBottomItems</code>{" "}
                in <code>src/routes.tsx</code> file.
              </Typography>
              <Box className="bg-grey-20 syntax-highlighter mt-3 rounded-lg p-4">
                <SyntaxHighlighter
                  className="bg-transparent!"
                  language="javascript"
                  style={isDarkMode ? atomOneDark : atomOneLight}
                  codeTagProps={{ className: "border-none" }}
                  showLineNumbers
                >
                  {`export const leftMenuItems: MenuItem[] = [
{
  id: "dashboards",
  icon: "NiHome",
  label: "menu-dashboards",
  description: "menu-dashboards-description",
  color: "text-primary",
  href: "/dashboards",
  children: [
    {
      id: "default",
      icon: "NiDashboard",
      label: "menu-default",
      href: "/dashboards/default",
      description: "menu-default-description",
    },
    {
      id: "analytics",
      icon: "NiChartPie",
      label: "menu-analytics",
      href: "/dashboards/analytics",
      description: "menu-analytics-description",
    },
    {
      id: "visual",
      icon: "NiPresentation",
      label: "menu-visual",
      href: "/dashboards/visual",
      description: "menu-visual-description",
    },
  ],
},
...`}
                </SyntaxHighlighter>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Navigating via React Router Dom Link
              </Typography>
              <Box className="bg-grey-20 syntax-highlighter rounded-lg p-4">
                <SyntaxHighlighter
                  className="bg-transparent!"
                  language="javascript"
                  style={isDarkMode ? atomOneDark : atomOneLight}
                  codeTagProps={{ className: "border-none" }}
                  showLineNumbers
                >
                  {`import { Link } from "react-router-dom";

import { Box } from "@mui/material";

export default function Page() {
  return (
    <Box className="flex flex-col">
      <Link to="/ui/navigation/link" className="link-primary">
        Link
      </Link>
      <Link to="https://themeforest.net" target="_blank" className="link-primary">
        MUI
      </Link>
    </Box>
  );
}`}
                </SyntaxHighlighter>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Navigating via useNavigate
              </Typography>
              <Box className="bg-grey-20 syntax-highlighter rounded-lg p-4">
                <SyntaxHighlighter
                  className="bg-transparent!"
                  language="javascript"
                  style={isDarkMode ? atomOneDark : atomOneLight}
                  codeTagProps={{ className: "border-none" }}
                  showLineNumbers
                >
                  {`import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

export default function Page() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/docs/getting-started/installation");
  }, [navigate]);
  return <></>;
}`}
                </SyntaxHighlighter>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Drawer open={openDrawer} anchor="right" onClose={toggleDrawer(false)}>
          <Box className="min-w-80 p-7">
            <MenuContent />
          </Box>
        </Drawer>
      </Grid>
    </Grid>
  );
}
