import { SyntheticEvent } from "react";
import { Link } from "react-router-dom";

import { Box, Breadcrumbs, Card, CardContent, Link as LinkMUI, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function Page() {
  const preventDefault = (event: SyntheticEvent) => event.preventDefault();

  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Link
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/navigation">
            Navigation
          </Link>
          <Typography variant="body2">Link</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Link
            </Typography>
            <Box onClick={preventDefault} className="flex flex-col items-start gap-2">
              <LinkMUI href="#">Primary</LinkMUI>
              <LinkMUI href="#" color="secondary">
                Secondary
              </LinkMUI>
              <LinkMUI href="#" color="textPrimary">
                Text Primary
              </LinkMUI>
              <LinkMUI href="#" color="textSecondary">
                Text Secondary
              </LinkMUI>
              <LinkMUI href="#" color="textDisabled">
                Text Disabled
              </LinkMUI>
              <LinkMUI href="#" color="info">
                Info
              </LinkMUI>
              <LinkMUI href="#" color="success">
                Success
              </LinkMUI>
              <LinkMUI href="#" color="warning">
                Warning
              </LinkMUI>
              <LinkMUI href="#" color="error">
                Error
              </LinkMUI>
              <LinkMUI href="#" variant="body1">
                Body 1
              </LinkMUI>
              <LinkMUI href="#" variant="button">
                Button
              </LinkMUI>
              <LinkMUI href="#" variant="body2">
                Body 2
              </LinkMUI>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Decoration
            </Typography>
            <Box onClick={preventDefault} className="flex flex-col items-start gap-2">
              <LinkMUI href="#" underline="none">
                None
              </LinkMUI>
              <LinkMUI href="#" underline="hover">
                Hover
              </LinkMUI>
              <LinkMUI href="#" underline="always">
                Always
              </LinkMUI>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              React Router Dom Link
            </Typography>
            <Box onClick={preventDefault} className="flex flex-col items-start gap-2">
              <Link to="/#" className="link-primary">
                Primary
              </Link>
              <Link to="/#" className="link-secondary">
                Secondary
              </Link>
              <Link to="/#" className="link-text-primary">
                Text Primary
              </Link>
              <Link to="/#" className="link-text-secondary">
                Text Secondary
              </Link>
              <Link to="/#" className="link-text-disabled">
                Text Disabled
              </Link>
              <Link to="/#" className="link-info">
                Info
              </Link>
              <Link to="/#" className="link-success">
                Success
              </Link>
              <Link to="/#" className="link-warning">
                Warning
              </Link>
              <Link to="/#" className="link-error">
                Error
              </Link>
              <Link to="/#" className="link-primary">
                Body 1
              </Link>
              <Link to="/#" className="link-primary link-button">
                Button
              </Link>
              <Link to="/#" className="link-primary link-body2">
                Body 2
              </Link>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              React Router Dom Link Decoration
            </Typography>
            <Box onClick={preventDefault} className="flex flex-col items-start gap-2">
              <Link to="/#" className="link-primary link-underline-none">
                None
              </Link>
              <Link to="/#" className="link-primary link-underline-hover">
                Hover
              </Link>
              <Link to="/#" className="link-primary">
                Always
              </Link>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

