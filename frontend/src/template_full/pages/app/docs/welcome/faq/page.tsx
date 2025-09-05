import DocsMenu from "../../sections/docs-menu";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Box, Breadcrumbs, Button, Card, CardContent, Drawer, Tooltip, Typography } from "@mui/material";
import { Grid } from "@mui/material";

import NiListCircle from "@/icons/nexture/ni-list-circle";

const MenuContent = () => {
  return (
    <Box className="flex flex-col gap-4">
      <DocsMenu selectedID="docs-faq" />
    </Box>
  );
};

export default function DocsWelcomeFaq() {
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
              FAQ
            </Typography>
            <Breadcrumbs>
              <Link color="inherit" to="/dashboards/default">
                Home
              </Link>
              <Link color="inherit" to="/docs">
                Docs
              </Link>
              <Link color="inherit" to="/docs/welcome">
                Welcome
              </Link>
              <Typography variant="body2">FAQ</Typography>
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
                Are the design files available?
              </Typography>
              <Box>
                <Typography variant="body1" component="p">
                  Yes, we have page designs and UI components in Figma. It is available with a Standard Plus or above
                  license and included with the project package.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Are the icons included within the source?
              </Typography>
              <Box>
                <Typography variant="body1" component="p">
                  Yes, they are both included in the code and Figma.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Are 3D artworks included within the source?
              </Typography>
              <Box>
                <Typography variant="body1" component="p">
                  We used Blender to create them and their sources are available with a Standard Plus license or above.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Which license is the correct one for me?
              </Typography>
              <Box>
                <Typography variant="body1" component="p">
                  If you are only interested in the Vite + React-router version, then the Standard License should cover
                  you. However, Next.js version is on the Standard Plus version. The extended license is only required
                  if the end product will be a SAAS(users need to pay to use the service) application.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Is the backend implemented?
              </Typography>
              <Box>
                <Typography variant="body1" component="p">
                  No, there are a couple of api calls which are responded to by a mock-api call. They are added only to
                  provide examples for some plugins and components.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Is authentication implemented?
              </Typography>
              <Box>
                <Typography variant="body1" component="p">
                  No, there is no authentication backend implementation in the template. Although, the template contains
                  authentication page layouts such as login, register, forgot password and reset password with
                  validation.
                </Typography>
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
