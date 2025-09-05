import { Box, Card, CardContent, Fab, Grid, Typography } from "@mui/material";

import NiBriefcase from "@/template_full/icons/nexture/ni-briefcase";

export default function FabColors() {
  return (
    <Grid size={12}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h5" className="card-title">
            Colors
          </Typography>

          <Box className="flex flex-col items-start gap-4">
            <Fab variant="extended" color="primary">
              <NiBriefcase className="mr-2" />
              Primary
            </Fab>
            <Fab variant="extended" color="secondary">
              <NiBriefcase className="mr-2" />
              Secondary
            </Fab>
            <Fab variant="extended" color="accent-1">
              <NiBriefcase className="mr-2" />
              Accent 1
            </Fab>
            <Fab variant="extended" color="accent-2">
              <NiBriefcase className="mr-2" />
              Accent 2
            </Fab>
            <Fab variant="extended" color="accent-3">
              <NiBriefcase className="mr-2" />
              Accent 3
            </Fab>
            <Fab variant="extended" color="accent-4">
              <NiBriefcase className="mr-2" />
              Accent 4
            </Fab>
            <Fab variant="extended" color="text-primary">
              <NiBriefcase className="mr-2" />
              Text Primary
            </Fab>
            <Fab variant="extended" color="text-secondary">
              <NiBriefcase className="mr-2" />
              Text Secondary
            </Fab>
            <Fab variant="extended" color="text-disabled">
              <NiBriefcase className="mr-2" />
              Text Disabled
            </Fab>
            <Fab variant="extended" color="info">
              <NiBriefcase className="mr-2" />
              Info
            </Fab>
            <Fab variant="extended" color="success">
              <NiBriefcase className="mr-2" />
              Success
            </Fab>
            <Fab variant="extended" color="warning">
              <NiBriefcase className="mr-2" />
              Warning
            </Fab>
            <Fab variant="extended" color="error">
              <NiBriefcase className="mr-2" />
              Error
            </Fab>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
}

