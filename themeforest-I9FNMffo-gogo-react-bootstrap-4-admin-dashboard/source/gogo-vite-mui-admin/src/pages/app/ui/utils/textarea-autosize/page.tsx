import TextareaAutosizeBasic from "./examples/textarea-autosize-basic";
import TextareaAutosizeMinMaxRows from "./examples/textarea-autosize-min-max-rows";
import { Link } from "react-router-dom";

import { Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Textarea Autosize
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/utils">
            Utils
          </Link>
          <Typography variant="body2">Textarea Autosize</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic
            </Typography>
            <TextareaAutosizeBasic />
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Min and Max Height
            </Typography>
            <TextareaAutosizeMinMaxRows />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
