import { Suspense } from "react";
import { useTranslation } from "react-i18next";
import { BrowserRouter } from "react-router-dom";

import { Box, StyledEngineProvider } from "@mui/material";

import BackgroundWrapper from "@/components/layout/containers/background-wrapper";
import SnackbarWrapper from "@/components/layout/containers/snackbar-wrapper";
import LayoutContextProvider from "@/components/layout/layout-context";
import Loading from "@/pages/loading";
import AppRoutes from "@/routes";
import ThemeProvider from "@/theme/theme-provider";
const App = () => {
  const { i18n } = useTranslation();

  return (
    <BrowserRouter>
      <StyledEngineProvider enableCssLayer>
        <Box lang={i18n.language} className="font-mulish font-urbanist relative overflow-hidden antialiased">
          {/* Initial loader */}
          <div id="initial-loader">
            <div className="spinner"></div>
          </div>
          {/* Initial loader end */}

          <ThemeProvider>
            <LayoutContextProvider>
              <BackgroundWrapper />
              <SnackbarWrapper>
                <Suspense fallback={<Loading />}>
                  {/* Routes */}
                  <AppRoutes />
                </Suspense>
              </SnackbarWrapper>
            </LayoutContextProvider>
          </ThemeProvider>
        </Box>
      </StyledEngineProvider>
    </BrowserRouter>
  );
};

export default App;
