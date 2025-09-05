import { Link } from "react-router-dom";

import { Box, Button, Card, CardContent, Grid, Typography } from "@mui/material";

import NiExternal from "@/template_full/icons/nexture/ni-external";
import NiInternal from "@/template_full/icons/nexture/ni-internal";

export default function ButtonLink() {
  return (
    <Grid size={12}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h5" className="card-title">
            Link Buttons
          </Typography>
          <Box className="flex flex-row gap-2">
            <Button
              variant="pastel"
              size="medium"
              color="primary"
              startIcon={<NiInternal size={20} />}
              to="/ui/inputs"
              component={Link}
            >
              React Router Dom Link
            </Button>
            <Button
              variant="pastel"
              size="medium"
              color="secondary"
              startIcon={<NiExternal size={20} />}
              to="https://themeforest.net"
              target="_blank"
              component={Link}
            >
              MUI Link
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
}

