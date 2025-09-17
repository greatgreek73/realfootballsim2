import { Link } from "react-router-dom";

import { Breadcrumbs, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function LevelFourSubs() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Level Four Subs
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/menu-levels">
            Menu Levels
          </Link>
          <Link color="inherit" to="/menu-levels/level-two-subs">
            Level Two Subs
          </Link>
          <Link color="inherit" to="/menu-levels/level-two-subs/level-three-subs">
            Level Three Subs
          </Link>
          <Typography variant="body2">Level Four Subs</Typography>
        </Breadcrumbs>
      </Grid>
    </Grid>
  );
}
