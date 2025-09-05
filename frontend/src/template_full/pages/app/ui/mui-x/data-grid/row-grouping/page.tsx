import RowGroupingBasic from "./examples/row-grouping-basic";
import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function RowGroupingPage() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Row Grouping
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/mui-x">
            MUI X
          </Link>
          <Link color="inherit" to="/ui/mui-x/data-grid">
            Data Grid
          </Link>
          <Typography variant="body2">Row Grouping</Typography>
        </Breadcrumbs>
      </Grid>
      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic
            </Typography>
            <RowGroupingBasic />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

