import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function SingleMenu() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Settings
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/home/sub">
            Home
          </Link>
          <Typography variant="body2">Settings</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid container size={12}>
        <Grid size={{ lg: 8, xs: 12 }}>
          <Card>
            <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
              Empty Card
            </Typography>
            <CardContent></CardContent>
          </Card>
        </Grid>

        <Grid size={{ lg: 4, xs: 12 }}>
          <Card>
            <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
              Empty Card
            </Typography>
            <CardContent></CardContent>
          </Card>
        </Grid>
      </Grid>
    </Grid>
  );
}
