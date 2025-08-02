import "@/i18n/i18n";
import "@/style/global.css";
import "@fontsource/mulish/latin.css";
import "@fontsource/urbanist/latin.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { LicenseInfo } from "@mui/x-license";

import App from "@/App";

LicenseInfo.setLicenseKey(import.meta.env.VITE_MUIX_LICENSE_KEY || "");

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
