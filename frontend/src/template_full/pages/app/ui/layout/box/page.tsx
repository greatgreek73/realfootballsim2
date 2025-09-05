import { Link } from "react-router-dom";

import { Box, Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Box
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/layout">
            Layout
          </Link>
          <Typography variant="body2">Box</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic
            </Typography>
            <Box className="border-grey-100 mb-2 rounded-md border border-solid p-4">
              This is a <code>division</code> rendered by a box component.
            </Box>
            <Box className="border-grey-100 mb-2 rounded-md border border-solid p-4" component="section">
              This is a <code>section</code> rendered by a box component.
            </Box>
            <Box className="border-grey-100 mb-0 rounded-md border border-solid p-4" component="p">
              This is a <code>paragraph</code> rendered by a box component.
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

