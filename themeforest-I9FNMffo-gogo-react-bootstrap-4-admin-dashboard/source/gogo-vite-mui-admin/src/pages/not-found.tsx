import { Link } from "react-router-dom";

import { Box, Button, Paper, Typography } from "@mui/material";

import Logo from "@/components/logo/logo";
import NiHome from "@/icons/nexture/ni-home";
import { cn } from "@/lib/utils";
import { useThemeContext } from "@/theme/theme-provider";

export default function Page() {
  const { isDarkMode } = useThemeContext();

  return (
    <Box className="flex min-h-screen w-full items-center justify-center p-4">
      <Paper
        elevation={3}
        className={cn(
          isDarkMode
            ? "bg-[url(/images/misc/error-background-dark.svg)]"
            : "bg-[url(/images/misc/error-background-light.svg)]",
          "bg-background-paper shadow-darker-xs min-h-[400px] max-w-full min-w-full items-center justify-center rounded-4xl bg-center py-14 md:min-w-[800px]",
        )}
      >
        <Box className="flex flex-col gap-4 px-8 sm:px-14">
          <Box className="flex flex-col">
            <Box className="mb-14 flex justify-center">
              <Logo classNameMobile="hidden" />
            </Box>

            <Box className="flex flex-col items-center gap-4">
              <Typography variant="h1" component="h1">
                Page not found!️
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Error Code: 404
              </Typography>
              <Button variant="outlined" startIcon={<NiHome />} to="/dashboards/default" component={Link}>
                Home
              </Button>
            </Box>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}
