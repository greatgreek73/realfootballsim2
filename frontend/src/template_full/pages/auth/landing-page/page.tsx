import LPAction from "./sections/lp-action";
import LPImage from "./sections/lp-image";
import LPInputs from "./sections/lp-inputs";
import LPLogos from "./sections/lp-logos";
import LPRatings from "./sections/lp-ratings";
import LPSettings from "./sections/lp-settings";
import LPStat from "./sections/lp-stat";
import LPTimeline from "./sections/lp-timeline";
import LPUser from "./sections/lp-user";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { Box, Button, Paper, Tooltip, Typography } from "@mui/material";

import Logo from "@/template_full/components/logo/logo";
import NiBasket from "@/template_full/icons/nexture/ni-basket";
import NiCatalog from "@/template_full/icons/nexture/ni-catalog";
import NiSendUpRight from "@/template_full/icons/nexture/ni-send-up-right";
import { cn } from "@/template_full/lib/utils";

export default function Page() {
  const { t } = useTranslation();

  return (
    <Box className="mx-auto flex h-dvh min-h-screen w-[100rem] max-w-full flex-col px-4 py-0">
      <Box className="flex h-16 w-full flex-none items-center justify-between">
        <Logo classNameMobile="hidden" />

        <Box className="flex flex-row gap-1">
          <Tooltip title={t("landing-view")} placement="bottom" arrow>
            <Button
              variant="surface"
              size="large"
              color="text-primary"
              className={cn("icon-only hover-icon-shrink [&.active]:text-primary")}
              startIcon={<NiSendUpRight size={24} />}
              to="/auth/sign-in"
              target="_blank"
              component={Link}
            />
          </Tooltip>
          <Tooltip title={t("landing-buy")} placement="bottom" arrow>
            <Button
              variant="surface"
              size="large"
              color="text-primary"
              className={cn("icon-only hover-icon-shrink [&.active]:text-primary")}
              startIcon={<NiBasket size={24} />}
              href="https://themeforest.net"
              target="_blank"
              component={"a"}
            />
          </Tooltip>
        </Box>
      </Box>
      <Paper
        elevation={3}
        className="bg-foreground outline-line h-full max-w-full rounded-4xl py-12 outline -outline-offset-1 backdrop-blur-md"
      >
        <Box className="flex h-full max-h-[calc(100dvh-12rem)] flex-col items-center gap-4 overflow-x-hidden overflow-y-auto px-10">
          <Box className="flex h-full min-h-[45rem] w-full max-w-[1200px] flex-1 flex-col items-center gap-10">
            <Box className="flex w-full flex-1 flex-col items-center gap-10 lg:flex-row 2xl:gap-20">
              {/* Text and Buttons */}
              <Box className="flex flex-0 flex-col text-center sm:min-w-sm lg:min-w-md lg:text-left">
                <Typography
                  component="h1"
                  variant="h1"
                  className="mb-7 text-[3rem] leading-12 font-extrabold md:text-[5rem] md:leading-20"
                >
                  {t("landing-create")}
                  <br />
                  {t("landing-beautiful")}
                  <br />
                  {t("landing-products")}
                </Typography>

                <Typography component="p" className="mb-4 max-w-xl text-[1.125rem] leading-6">
                  {t("landing-copy")}
                </Typography>
                <Box className="flex flex-row justify-center gap-2 lg:justify-start">
                  <Button
                    size="large"
                    color="primary"
                    variant="contained"
                    startIcon={<NiSendUpRight size={"large"} />}
                    to="/auth/sign-in"
                    target="_blank"
                    component={Link}
                  >
                    {t("landing-view-live")}
                  </Button>

                  <Button
                    size="large"
                    color="primary"
                    variant="pastel"
                    startIcon={<NiCatalog size={"large"} />}
                    href="https://www.figma.com/design/CCUQejXdGzW2wMj2SCt8Sz/Gogo-Design---Preview?node-id=1381-11546&t=ZvHFuhjjUoY6u9ul-1"
                    target="_blank"
                    component={"a"}
                  >
                    {t("landing-figma")}
                  </Button>
                </Box>
              </Box>

              {/* UI Elements */}
              <Box className="flex flex-1 flex-row items-start justify-end gap-2.5 lg:items-center">
                <Box className="flex flex-none flex-col items-end gap-2.5">
                  <LPStat />
                  <LPAction />
                  <LPUser />
                  <LPTimeline />
                </Box>
                <Box className="flex flex-none flex-col items-start gap-2.5">
                  <LPImage />
                  <LPSettings />
                  <LPInputs />
                  <LPRatings />
                </Box>
              </Box>
            </Box>

            <Box className="mb-8 flex h-9 w-full flex-none flex-row justify-center">
              <LPLogos />
            </Box>
          </Box>
        </Box>
      </Paper>
      <Box className="flex h-10 w-full items-center justify-center">
        <Button
          size="tiny"
          color="text-secondary"
          variant="text"
          className="hover:text-primary !bg-transparent font-normal"
          to="/"
          target="_blank"
          component={Link}
        >
          {t("footer-live")}
        </Button>
        <Button
          size="tiny"
          color="text-secondary"
          variant="text"
          className="hover:text-primary !bg-transparent font-normal"
          to="/docs"
          target="_blank"
          component={Link}
        >
          {t("footer-docs")}
        </Button>
        <Button
          size="tiny"
          color="text-secondary"
          variant="text"
          className="hover:text-primary !bg-transparent font-normal"
          href="https://themeforest.net"
          target="_blank"
          component={"a"}
        >
          {t("footer-purchase")}
        </Button>
      </Box>
    </Box>
  );
}

