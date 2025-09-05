import SpeedDialBasic from "./examples/speed-dial-basic";
import SpeedDialControlled from "./examples/speed-dial-controlled";
import SpeedDialCustomIcon from "./examples/speed-dial-custom-icon";
import SpeedDialPosition from "./examples/speed-dial-position";
import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Speed Dial
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
          <Typography variant="body2">Speed Dial</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic
            </Typography>
            <SpeedDialBasic></SpeedDialBasic>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Position
            </Typography>
            <SpeedDialPosition></SpeedDialPosition>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Controlled
            </Typography>
            <SpeedDialControlled></SpeedDialControlled>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Custom Close Icon
            </Typography>
            <SpeedDialCustomIcon></SpeedDialCustomIcon>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

