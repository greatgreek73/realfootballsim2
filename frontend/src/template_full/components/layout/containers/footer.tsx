import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { Box, Button } from "@mui/material";

export default function Footer() {
  const { t } = useTranslation();

  return (
    <Box component="footer" className="flex h-10 items-center justify-center">
      <Button
        size="tiny"
        color="text-secondary"
        variant="text"
        className="hover:text-primary !bg-transparent font-normal"
        component={Link}
        to="/"
      >
        {t("footer-about")}
      </Button>
      <Button
        size="tiny"
        color="text-secondary"
        variant="text"
        className="hover:text-primary !bg-transparent font-normal"
        component={Link}
        to="/docs"
      >
        {t("footer-docs")}
      </Button>
      <Button
        size="tiny"
        color="text-secondary"
        variant="text"
        className="hover:text-primary !bg-transparent font-normal"
        component={Link}
        to="https://themeforest.net"
        target="_blank"
      >
        {t("footer-purchase")}
      </Button>
    </Box>
  );
}

