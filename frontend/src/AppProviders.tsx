import React from "react";
import {
  ThemeProvider,
  CssBaseline,
  createTheme,
} from "@mui/material";
import { SnackbarProvider } from "notistack";
import { LocalizationProvider } from "@mui/x-date-pickers-pro/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers-pro/AdapterDayjs";

// Временная заглушка вместо react-helmet-async (пакет сняли)
const HelmetProvider: React.FC<React.PropsWithChildren> = ({ children }) => <>{children}</>;

// Минимальная валидная тема (важно: НЕ undefined)
const theme = createTheme({
  typography: {
    fontFamily: 'Mulish, ui-sans-serif',
  },
});

export default function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <HelmetProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <SnackbarProvider maxSnack={3}>{children}</SnackbarProvider>
        </LocalizationProvider>
      </ThemeProvider>
    </HelmetProvider>
  );
}
