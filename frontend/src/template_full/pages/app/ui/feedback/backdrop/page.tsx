import { useState } from "react";
import { Link } from "react-router-dom";

import {
  Backdrop,
  Box,
  Breadcrumbs,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Portal,
  Typography,
} from "@mui/material";
import { Grid } from "@mui/material";

export default function Page() {
  const [open, setOpen] = useState(false);
  const handleClose = () => {
    setOpen(false);
  };
  const handleOpen = () => {
    setOpen(true);
  };

  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Backdrop
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/feedback">
            Feedback
          </Link>
          <Typography variant="body2">Backdrop</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Example
            </Typography>
            <Box>
              <Button onClick={handleOpen} variant="pastel">
                Show Backdrop
              </Button>
              <Portal>
                <Backdrop className="text-text-contrast z-1201" open={open} onClick={handleClose}>
                  <CircularProgress color="inherit" />
                </Backdrop>
              </Portal>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

