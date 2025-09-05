import { Link } from "react-router-dom";

import { Breadcrumbs, Typography } from "@mui/material";
import { Grid } from "@mui/material";

import ListingPageContent from "@/components/layout/listing-page-content";

export default function Lab() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Lab
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Typography variant="body2">Lab</Typography>
        </Breadcrumbs>
      </Grid>

      <ListingPageContent />
    </Grid>
  );
}
