import BottomNavigationAbsolute from "./examples/bottom-navigation-absolute";
import BottomNavigationBasic from "./examples/bottom-navigation-basic";
import BottomNavigationNoLabel from "./examples/bottom-navigation-no-label";
import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default async function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Bottom Navigation
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/navigation">
            Navigation
          </Link>
          <Typography variant="body2">Bottom Navigation</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic
            </Typography>
            <BottomNavigationBasic />
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              No Label
            </Typography>
            <BottomNavigationNoLabel />
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Absolute Positioned
            </Typography>
            <BottomNavigationAbsolute />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

