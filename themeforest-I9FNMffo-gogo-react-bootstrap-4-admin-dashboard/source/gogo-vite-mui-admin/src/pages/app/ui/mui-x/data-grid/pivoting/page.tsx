import PivotingBasic from "./examples/pivoting-basic";
import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function PivotingPage() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Pivoting
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
          <Typography variant="body2">Pivoting</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <PivotingBasic />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
