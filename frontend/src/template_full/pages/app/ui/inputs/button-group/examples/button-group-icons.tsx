import { Box, Button, ButtonGroup, Card, CardContent, Grid, Typography } from "@mui/material";

import NiFloppyDisk from "@/template_full/icons/nexture/ni-floppy-disk";
import NiSendRight from "@/template_full/icons/nexture/ni-send-right";
import NiShare from "@/template_full/icons/nexture/ni-share";

export default function ButtonGroupIcons() {
  return (
    <Grid size={12}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h5" className="card-title">
            Icons
          </Typography>
          <Box className="row mb-4 flex flex-wrap items-start gap-2">
            <ButtonGroup variant="pastel" color="text-primary">
              <Button startIcon={<NiSendRight size={"medium"} />}>Reply</Button>
              <Button startIcon={<NiFloppyDisk size={"medium"} />}>Save</Button>
              <Button startIcon={<NiShare size={"medium"} />}>Share</Button>
            </ButtonGroup>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
}

