import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Grid, Typography } from "@mui/material";

import BasicGauge from "@/pages/app/ui/mui-x/charts/gauge/examples/basic-gauge";
import Pointer from "@/pages/app/ui/mui-x/charts/gauge/examples/pointer";

export default function GaugeCharts() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Gauge Charts
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui/mui-x">
            MUI X
          </Link>
          <Link color="inherit" to="/ui/mui-x/charts">
            Charts
          </Link>
          <Typography variant="body2">Gauge</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic Gauge Charts
            </Typography>
            <BasicGauge />
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Pointer
            </Typography>
            <Pointer />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
