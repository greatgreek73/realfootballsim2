import { Box, Button, Card, CardContent, Grid, Typography } from "@mui/material";

import NiBag from "@/template_full/icons/nexture/ni-bag";
import NiCrown from "@/template_full/icons/nexture/ni-crown";
import NiHome from "@/template_full/icons/nexture/ni-home";
import NiKnobs from "@/template_full/icons/nexture/ni-knobs";
import NiStars from "@/template_full/icons/nexture/ni-stars";

export default function ButtonFocusable() {
  return (
    <Grid size={12}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h5" className="card-title">
            Focusable and Focus from Form Container
          </Typography>
          <Box className="row mb-4 flex flex-wrap items-start gap-2">
            <Button
              size="medium"
              color="primary"
              variant="contained"
              startIcon={<NiHome size={"medium"} />}
              className="focusable"
            >
              Focus
            </Button>
            <Button
              size="medium"
              color="primary"
              variant="outlined"
              startIcon={<NiBag size={"medium"} />}
              className="focusable"
            >
              Focus
            </Button>
            <Button
              size="medium"
              color="primary"
              variant="pastel"
              startIcon={<NiCrown size={"medium"} />}
              className="focusable"
            >
              Focus
            </Button>
            <Button
              size="medium"
              color="primary"
              variant="text"
              startIcon={<NiKnobs size={"medium"} />}
              className="focusable"
            >
              Focus
            </Button>
            <Button
              size="medium"
              color="primary"
              variant="surface"
              startIcon={<NiStars size={"medium"} />}
              className="focusable"
            >
              Focus
            </Button>
          </Box>
          <Box className="row mb-4 flex flex-wrap items-start gap-2" component="form">
            <Button size="medium" color="primary" variant="contained" startIcon={<NiHome size={"medium"} />}>
              Focus
            </Button>
            <Button size="medium" color="primary" variant="outlined" startIcon={<NiBag size={"medium"} />}>
              Focus
            </Button>
            <Button size="medium" color="primary" variant="pastel" startIcon={<NiCrown size={"medium"} />}>
              Focus
            </Button>
            <Button size="medium" color="primary" variant="text" startIcon={<NiKnobs size={"medium"} />}>
              Focus
            </Button>
            <Button size="medium" color="primary" variant="surface" startIcon={<NiStars size={"medium"} />}>
              Focus
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
}

