import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Grid, Typography } from "@mui/material";

import BasicBar from "@/template_full/pages/app/ui/mui-x/charts/bars/examples/basic-bar";
import Stacking from "@/template_full/pages/app/ui/mui-x/charts/bars/examples/stacking";
import UsingADataset from "@/template_full/pages/app/ui/mui-x/charts/bars/examples/using-a-dataset";

export default function BarsCharts() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Bars Charts
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
          <Typography variant="body2">Bars</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic Bar Chart
            </Typography>
            <BasicBar />
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Using a Dataset
            </Typography>
            <UsingADataset />
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Stacking
            </Typography>
            <Stacking />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

