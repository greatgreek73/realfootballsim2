import { Box, Button, Card, CardContent, Typography } from "@mui/material";

import IllustrationConfigure from "@/icons/illustrations/illustration-configure";
import NiPalette from "@/icons/nexture/ni-palette";

export default function DashboardDefaultBanner() {
  const handleConfigureButtonClick = () => {
    const themeCustomizationButton = document.getElementById("theme-customization");
    if (themeCustomizationButton) {
      themeCustomizationButton.click();
    }
  };
  return (
    <Card className="h-full">
      <CardContent className="flex h-full flex-col items-start justify-between">
        <Box className="flex w-full flex-col md:flex-row">
          <Box className="w-full md:w-6/12 xl:w-8/12">
            <Typography variant="h4" component="h4" className="card-title">
              Configure the Theme
            </Typography>
            <Typography
              variant="body1"
              component="p"
              className="text-text-secondary text-center md:text-left xl:max-w-md"
            >
              Configuring theme colors and background options allows you to personalize the theme. You can also change
              the menu type, and switch between fluid and boxed layout.
            </Typography>
          </Box>
          <Box className="flex w-full justify-center md:w-6/12 md:justify-end xl:w-4/12">
            <IllustrationConfigure className="text-primary h-64 w-full max-w-xs object-contain" />
          </Box>
        </Box>
        <Button
          className="mx-auto md:mx-0"
          size="medium"
          color="primary"
          variant="contained"
          startIcon={<NiPalette size={"medium"} />}
          onClick={handleConfigureButtonClick}
        >
          Configure
        </Button>
      </CardContent>
    </Card>
  );
}
