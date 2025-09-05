import { Link } from "react-router-dom";

import { Breadcrumbs, Typography } from "@mui/material";
import { Grid } from "@mui/material";

import ListingPageContent from "@/template_full/components/layout/listing-page-content";

export default function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Pages
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Typography variant="body2">Pages</Typography>
        </Breadcrumbs>
      </Grid>

      <ListingPageContent />
    </Grid>
  );
}

