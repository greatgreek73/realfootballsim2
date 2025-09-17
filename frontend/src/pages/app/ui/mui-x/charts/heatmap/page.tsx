import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Grid, Typography } from "@mui/material";

import BasicHeatmap from "@/pages/app/ui/mui-x/charts/heatmap/examples/basic-heatmap";

export default function HeatmapCharts() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Heatmap Charts
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
          <Typography variant="body2">Heatmap</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic Heatmap Chart
            </Typography>
            <BasicHeatmap />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
