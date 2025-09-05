import { Link } from "react-router-dom";

import { Breadcrumbs, Button, Grid, Typography } from "@mui/material";

import NiEllipsisHorizontal from "@/template_full/icons/nexture/ni-ellipsis-horizontal";

export default function Page() {
  return (
    <Grid container spacing={5} className="w-full" size={12}>
      <Grid size={12} container spacing={2.5}>
        <Grid size={{ xs: 12, md: "grow" }}>
          <Typography variant="h1" component="h1" className="mb-0">
            Empty
          </Typography>
          <Breadcrumbs>
            <Link color="inherit" to="/dashboards/default">
              Home
            </Link>
            <Link color="inherit" to="/pages">
              Pages
            </Link>
            <Link color="inherit" to="/pages/miscellaneous">
              Miscellaneous
            </Link>
            <Typography variant="body2">Empty</Typography>
          </Breadcrumbs>
        </Grid>
        <Grid size={{ xs: 12, md: "auto" }}>
          <Button className="icon-only surface-standard" color="grey" variant="surface">
            <NiEllipsisHorizontal size={"medium"} />
          </Button>
        </Grid>
      </Grid>

      <Grid size={12}></Grid>
    </Grid>
  );
}

