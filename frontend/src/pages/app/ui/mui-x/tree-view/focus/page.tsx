import FocusItemRich from "./examples/focus-item-rich";
import FocusItemSimple from "./examples/focus-item-simple";
import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function Overview() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Focus
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
          <Link color="inherit" to="/ui/mui-x/tree-view">
            Tree View
          </Link>
          <Typography variant="body2">Focus</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Focus Item - Simple
            </Typography>
            <FocusItemSimple />
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Focus Item - Rich
            </Typography>
            <FocusItemRich />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
