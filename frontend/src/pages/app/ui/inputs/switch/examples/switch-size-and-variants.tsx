import { Box, Card, CardContent, FormControl, FormControlLabel, Grid, Switch, Typography } from "@mui/material";

export default function SwitchSizeAndVariants() {
  return (
    <Grid size={12}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h5" className="card-title">
            Size and Variants
          </Typography>
          <Box className="flex flex-col">
            <FormControl>
              <FormControlLabel control={<Switch size="small" />} label="Small" />
            </FormControl>
            <FormControl>
              <FormControlLabel control={<Switch size="small" className="outlined" />} label="Small Outlined" />
            </FormControl>
            <FormControl>
              <FormControlLabel control={<Switch />} label="Medium" />
            </FormControl>
            <FormControl>
              <FormControlLabel control={<Switch className="outlined" />} label="Medium Outlined" />
            </FormControl>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
}
