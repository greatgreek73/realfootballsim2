import { Card, CardContent, FormGroup, FormLabel, Grid, Rating, Typography } from "@mui/material";

import NiStar from "@/template_full/icons/nexture/ni-star";

export default function RatingSizes() {
  return (
    <Grid size={12}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h5" className="card-title">
            Sizes
          </Typography>

          <FormGroup>
            <FormLabel component="label">Small</FormLabel>
            <Rating
              size="small"
              defaultValue={4}
              max={5}
              icon={<NiStar variant="contained" size="small" className="contained" />}
              emptyIcon={<NiStar size="small" className="contained" />}
            />
          </FormGroup>
          <FormGroup>
            <FormLabel component="label">Medium</FormLabel>
            <Rating
              defaultValue={4}
              max={5}
              icon={<NiStar variant="contained" size="medium" className="contained" />}
              emptyIcon={<NiStar size="medium" className="contained" />}
            />
          </FormGroup>
          <FormGroup>
            <FormLabel component="label">Large</FormLabel>
            <Rating
              size="large"
              defaultValue={4}
              max={5}
              icon={<NiStar variant="contained" size="large" className="contained" />}
              emptyIcon={<NiStar size="large" className="contained" />}
            />
          </FormGroup>
        </CardContent>
      </Card>
    </Grid>
  );
}

