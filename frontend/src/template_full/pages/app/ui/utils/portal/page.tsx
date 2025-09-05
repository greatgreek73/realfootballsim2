import PortalContainer from "./examples/portal-container";
import PortalNoContainer from "./examples/portal-no-container";
import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Portal
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/utils">
            Utils
          </Link>
          <Typography variant="body2">Portal</Typography>
        </Breadcrumbs>
      </Grid>

      <PortalContainer />

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              No Container
            </Typography>
            <PortalNoContainer />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

