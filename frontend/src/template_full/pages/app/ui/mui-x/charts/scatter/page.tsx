import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Grid, Typography } from "@mui/material";

import BasicScatter from "@/template_full/pages/app/ui/mui-x/charts/scatter/examples/basic-scatter";
import MultipleYAxis from "@/template_full/pages/app/ui/mui-x/charts/scatter/examples/multiple-y-axis";

export default function ScatterCharts() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Scatter Charts
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
          <Typography variant="body2">Scatter</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic Scatter Chart
            </Typography>
            <BasicScatter />
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Multiple Y Axis
            </Typography>
            <MultipleYAxis />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

