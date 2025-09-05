import { useLayoutContext } from "../layout-context";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Button, Divider, Drawer, Tooltip, Typography } from "@mui/material";

import { DEFAULTS } from "@/template_full/config";
import { ModeVariant, THEME_OPTIONS } from "@/template_full/constants";
import { RadiobuttonSmallChecked, RadiobuttonSmallEmptyOutlined } from "@/template_full/icons/form/mui-radiobutton";
import NiArrowCircleLeft from "@/template_full/icons/nexture/ni-arrow-circle-left";
import NiBasket from "@/template_full/icons/nexture/ni-basket";
import NiChevronLeftRightReverseSmall from "@/template_full/icons/nexture/ni-chevron-left-right-reverse-small";
import NiChevronLeftRightSmall from "@/template_full/icons/nexture/ni-chevron-left-right-small";
import NiKnobs from "@/template_full/icons/nexture/ni-knobs";
import NiMenu from "@/template_full/icons/nexture/ni-menu";
import NiMenuSplit from "@/template_full/icons/nexture/ni-menu-split";
import NiMenuSplitDot from "@/template_full/icons/nexture/ni-menu-split-dot";
import NiMoon from "@/template_full/icons/nexture/ni-moon";
import NiPalette from "@/template_full/icons/nexture/ni-palette";
import NiScreen from "@/template_full/icons/nexture/ni-screen";
import NiSun from "@/template_full/icons/nexture/ni-sun";
import { cn } from "@/template_full/lib/utils";
import { useThemeContext } from "@/template_full/theme/theme-provider";
import { ContentType, MenuType } from "@/template_full/types/types";

export default function ThemeConfiguration() {
  const [openDrawer, setOpenDrawer] = useState(false);

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpenDrawer(newOpen);
  };

  const { t } = useTranslation();

  const { theme, setTheme, mode, setMode, content, setContent } = useThemeContext();
  const { leftMenuType, setLeftMenuType } = useLayoutContext();

  const handleResetTheme = () => {
    setTheme(DEFAULTS.themeColor);
    setMode(DEFAULTS.themeMode);
    setContent(DEFAULTS.contentType);
    setLeftMenuType(DEFAULTS.leftMenuType);
  };

  const themeModeOptions = [
    { value: "system" as ModeVariant, icon: <NiScreen /> },
    { value: "light" as ModeVariant, icon: <NiSun /> },
    { value: "dark" as ModeVariant, icon: <NiMoon /> },
  ];

  const leftMenuOptions = [
    { value: MenuType.Minimal, icon: <NiMenuSplitDot /> },
    { value: MenuType.Comfort, icon: <NiMenuSplit /> },
    { value: MenuType.SingleLayer, icon: <NiMenu /> },
  ];

  const contentOptions = [
    { value: ContentType.Boxed, icon: <NiChevronLeftRightReverseSmall /> },
    { value: ContentType.Fluid, icon: <NiChevronLeftRightSmall /> },
  ];

  return (
    <>
      <Box className="bg-background-paper shadow-darker-xs fixed top-1/2 right-0 flex w-[60px] -translate-y-1/2 flex-col gap-2 rounded-l-3xl p-2.5">
        <Tooltip title="Configuration" placement="left" arrow>
          <Button
            onClick={toggleDrawer(true)}
            className="icon-only text-primary"
            size="large"
            color="grey"
            variant="text"
            startIcon={<NiKnobs size={"large"} />}
          ></Button>
        </Tooltip>
        <Tooltip title="Purchase" placement="left" arrow>
          <Button
            className="icon-only text-secondary"
            size="large"
            color="grey"
            variant="text"
            startIcon={<NiBasket size={"large"} />}
            href="https://themeforest.net"
            target="_blank"
          ></Button>
        </Tooltip>
      </Box>
      <Drawer open={openDrawer} anchor="right" onClose={toggleDrawer(false)}>
        <Box className="flex min-h-full min-w-80 flex-col p-5">
          <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
            Configuration
          </Typography>

          <Box className="mb-4 flex flex-1 flex-col gap-2 px-5">
            <Typography variant="body2" className="font-semibold" component="div">
              {t("palette")}
            </Typography>
            <Box className="flex flex-col gap-2">
              {Object.values(THEME_OPTIONS).map((option) => (
                <Button
                  key={`theme-color-${option}`}
                  className={cn(
                    "full-width-button hover:bg-grey-25! flex justify-between shadow-none! outline-none!",
                    option,
                    theme === option && "active bg-grey-25!",
                  )}
                  variant="surface"
                  startIcon={<NiPalette />}
                  onClick={() => setTheme(option)}
                >
                  {t(option)}
                  <span className={cn("flex flex-1 justify-end", theme !== option && "text-grey-200")}>
                    {theme === option && <RadiobuttonSmallChecked />}
                    {theme !== option && <RadiobuttonSmallEmptyOutlined />}
                  </span>
                </Button>
              ))}
            </Box>
            <Divider />
            <Typography variant="body2" component="div" className="font-semibold">
              {t("mode")}
            </Typography>
            <Box className="flex flex-col gap-2">
              {themeModeOptions.map((option) => (
                <Button
                  key={`theme-mode-${option.value}`}
                  className={cn(
                    "full-width-button hover:bg-grey-25! flex justify-between shadow-none! outline-none!",
                    mode === option.value && "active bg-grey-25!",
                  )}
                  variant="surface"
                  color={mode === option.value ? "primary" : "text-primary"}
                  startIcon={option.icon}
                  onClick={() => setMode(option.value)}
                >
                  {t(`mode-${option.value}`)}
                  <span className={cn("flex flex-1 justify-end", mode !== option.value && "text-grey-200")}>
                    {mode === option.value && <RadiobuttonSmallChecked />}
                    {mode !== option.value && <RadiobuttonSmallEmptyOutlined />}
                  </span>
                </Button>
              ))}
            </Box>

            <Divider />
            <Typography variant="body2" component="div" className="font-semibold">
              {t("left-menu")}
            </Typography>
            <Box className="flex flex-col gap-2">
              {leftMenuOptions.map((option) => (
                <Button
                  key={`theme-left-menu-${option.value}`}
                  className={cn(
                    "full-width-button hover:bg-grey-25! flex justify-between shadow-none! outline-none!",
                    leftMenuType === option.value && "active bg-grey-25!",
                  )}
                  variant="surface"
                  color={leftMenuType === option.value ? "primary" : "text-primary"}
                  startIcon={option.icon}
                  onClick={() => setLeftMenuType(option.value)}
                >
                  {t(`menu-${option.value}`)}
                  <span className={cn("flex flex-1 justify-end", leftMenuType !== option.value && "text-grey-200")}>
                    {leftMenuType === option.value && <RadiobuttonSmallChecked />}
                    {leftMenuType !== option.value && <RadiobuttonSmallEmptyOutlined />}
                  </span>
                </Button>
              ))}
            </Box>

            <Divider />
            <Typography variant="body2" component="div" className="font-semibold">
              {t("content")}
            </Typography>
            <Box className="flex flex-col gap-2">
              {contentOptions.map((option) => (
                <Button
                  key={`theme-content-${option.value}`}
                  className={cn(
                    "full-width-button hover:bg-grey-25! flex justify-between shadow-none! outline-none!",
                    content === option.value && "active bg-grey-25!",
                  )}
                  variant="surface"
                  color={content === option.value ? "primary" : "text-primary"}
                  startIcon={option.icon}
                  onClick={() => setContent(option.value)}
                >
                  {t(`content-${option.value}`)}
                  <span className={cn("flex flex-1 justify-end", content !== option.value && "text-grey-200")}>
                    {content === option.value && <RadiobuttonSmallChecked />}
                    {content !== option.value && <RadiobuttonSmallEmptyOutlined />}
                  </span>
                </Button>
              ))}
            </Box>
          </Box>
          <Box className="mt-auto flex w-full px-5 pb-4">
            <Button
              variant="outlined"
              size="small"
              color="grey"
              startIcon={<NiArrowCircleLeft size="small" />}
              className="w-full"
              onClick={() => handleResetTheme()}
            >
              {t("reset-theme")}
            </Button>
          </Box>
        </Box>
      </Drawer>
    </>
  );
}

