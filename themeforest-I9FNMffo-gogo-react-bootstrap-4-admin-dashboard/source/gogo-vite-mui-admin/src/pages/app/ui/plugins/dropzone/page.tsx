import DropzoneStandard from "./examples/dropzone-standard";
import DropzoneStandardOutlined from "./examples/dropzone-standard-outlined";
import { Link } from "react-router-dom";

import { Breadcrumbs, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Dropzone
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/plugins">
            Plugins
          </Link>
          <Typography variant="body2">Dropzone</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <DropzoneStandard />
      </Grid>
      <Grid size={12}>
        <DropzoneStandardOutlined />
      </Grid>
    </Grid>
  );
}
