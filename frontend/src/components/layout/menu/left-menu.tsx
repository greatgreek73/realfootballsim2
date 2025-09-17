import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { Box, Paper, Typography } from "@mui/material";

import { useLayoutContext } from "@/components/layout/layout-context";
import { PrimaryItem } from "@/components/layout/menu/primary-item";
import { SecondaryItem } from "@/components/layout/menu/secondary-item";
import { DEFAULTS } from "@/config";
import IllustrationLaunch from "@/icons/illustrations/illustration-launch";
import { cn, isPathMatch } from "@/lib/utils";
import { leftMenuBottomItems, leftMenuItems } from "@/menu-items";
import { MenuItem, MenuShowState, MenuType } from "@/types/types";

export type OpenedAccordion = { indent: number; id: string };

type MenuTrailNode = { item: MenuItem; depth: number };

const hasVisibleChildren = (item?: MenuItem): boolean =>
  !!item?.children?.some((child) => !child.hideInMenu);

function findMenuTrail(
  menu: MenuItem[],
  pathname: string,
  depth = 0,
): MenuTrailNode[] | null {
  for (const item of menu) {
    if (item.hideInMenu) continue;

    const current: MenuTrailNode = { item, depth };

    if (item.children?.length) {
      const childTrail = findMenuTrail(item.children, pathname, depth + 1);
      if (childTrail) return [current, ...childTrail];
    }

    if (item.href && isPathMatch(pathname, item.href)) {
      return [current];
    }
  }

  return null;
}

export default function LeftMenu() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const {
    leftMenuType,
    leftMenuWidth,
    leftPrimaryCurrent,
    leftSecondaryCurrent,
    showLeftSecondary,
    hideLeftSecondary,
    resetLeftMenu,
    onResetLeft,
    leftShowBackdrop,
    setLeftShowBackdrop,
  } = useLayoutContext();

  const selectedPrimary = useRef<undefined | MenuItem>(undefined);
  const [activeItem, setActiveItem] = useState<MenuItem | undefined>(undefined);
  const [openedAccordions, setOpenedAccordions] = useState<OpenedAccordion[]>([]);

  const activeTrail = useMemo(
    () =>
      findMenuTrail(leftMenuItems, pathname) ?? findMenuTrail(leftMenuBottomItems, pathname),
    [pathname],
  );

  useEffect(() => {
    const top = activeTrail?.[0]?.item;
    selectedPrimary.current = top;
    setActiveItem(top);

    const accordions =
      activeTrail
        ?.slice(1)
        .filter((node) => hasVisibleChildren(node.item))
        .map((node) => ({
          indent: Math.max(0, node.depth - 1),
          id: node.item.id,
        })) ?? [];

    setOpenedAccordions(accordions);
    resetLeftMenu();
  }, [activeTrail, resetLeftMenu]);

  useEffect(() => {
    if (selectedPrimary.current?.id !== activeItem?.id && !leftShowBackdrop) {
      setLeftShowBackdrop(true);
    }
  }, [activeItem?.id, selectedPrimary.current?.id, setLeftShowBackdrop, leftShowBackdrop]);

  useEffect(() => {
    const resetCallback = () => {
      if (selectedPrimary.current) {
        setActiveItem(selectedPrimary.current);
        if (
          !selectedPrimary.current.children ||
          !selectedPrimary.current.children.filter((x) => !x.hideInMenu).length
        ) {
          hideLeftSecondary();
        }
      }
    };

    onResetLeft(resetCallback);

    return () => {
      onResetLeft(() => {});
    };
  }, [onResetLeft, hideLeftSecondary]);

  useEffect(() => {
    if (activeItem && hasVisibleChildren(activeItem)) {
      showLeftSecondary();
    }
  }, [activeItem, showLeftSecondary]);

  const handleSelectPrimaryItem = (item: MenuItem) => {
    setActiveItem(item);
    if (item.children && item.children.filter((x) => !x.hideInMenu).length > 0) {
      showLeftSecondary();
    } else {
      // close all opened accordions
      // if the item is the same as the current path, hide the secondary menu and reset the left menu
      const isSameExactPath = !!item.href && pathname.replace(/\/$/, "") === item.href.replace(/\/$/, "");
      if (isSameExactPath) {
        hideLeftSecondary();
        resetLeftMenu();
      } else {
        setOpenedAccordions([]);
        if (item.href) navigate(item.href);
      }
    }
  };

  useEffect(() => {
    if (!activeItem?.children && leftSecondaryCurrent === MenuShowState.Hide) {
      hideLeftSecondary();
    }
  }, [activeItem, hideLeftSecondary, leftSecondaryCurrent]);

  const leftSecondaryDefaultWidth = useMemo(() => DEFAULTS.leftMenuWidth[leftMenuType].secondary, [leftMenuType]);

  return (
    <nav className="bg-background-paper shadow-darker-xs fixed z-10 mt-20 flex h-[calc(100%-5rem)] flex-row rounded-r-3xl">
      <Box
        className={cn(
          "flex h-full shrink-0 grow-0 flex-col items-center overflow-x-hidden py-2.5! transition-all duration-(--layout-duration)",
        )}
        style={{
          ...(leftPrimaryCurrent !== MenuShowState.Hide && leftMenuWidth.primary > 0
            ? { width: `${leftMenuWidth.primary}px` }
            : { width: "0px" }),
        }}
      >
        <Box
          className={cn(
            leftMenuType === MenuType.SingleLayer && "overflow-y-scroll px-4 py-2",
            "absolute flex h-full min-h-full shrink-0 grow-0 flex-col items-center gap-0.5 overflow-y-auto",
          )}
          style={{ width: `${leftMenuWidth.primary}px` }}
        >
          <Box className={cn("flex flex-1 flex-col gap-0.5")}>
            {leftMenuItems
              .filter((x) => !x.hideInMenu)
              .map((item) =>
                leftMenuType !== MenuType.SingleLayer ? (
                  <PrimaryItem
                    className={cn(leftShowBackdrop && "z-20")}
                    item={item}
                    key={`left-menu-primary-item-${leftMenuType}-${item.id}`}
                    onSelect={(item) => handleSelectPrimaryItem(item)}
                    isActive={activeItem?.id === item.id}
                    menuType={leftMenuType}
                  />
                ) : (
                  <SecondaryItem
                    className={cn(leftShowBackdrop && "z-20")}
                    item={item}
                    key={`left-menu-primary-item-${leftMenuType}-${item.id}`}
                    indent={0}
                    openedAccordions={openedAccordions}
                    setOpenedAccordions={setOpenedAccordions}
                  />
                ),
              )}
          </Box>
          <Box className={cn("mb-5 flex w-full flex-col items-center gap-0.5")}>
            {leftMenuBottomItems
              .filter((x) => !x.hideInMenu)
              .map((item) =>
                leftMenuType !== MenuType.SingleLayer ? (
                  <PrimaryItem
                    className={cn(leftShowBackdrop && "z-20")}
                    item={item}
                    key={`left-menu-bottom-item-${leftMenuType}-${item.id}`}
                    onSelect={(item) => handleSelectPrimaryItem(item)}
                    isActive={activeItem?.id === item.id}
                    menuType={leftMenuType}
                  />
                ) : (
                  <SecondaryItem
                    className={cn(leftShowBackdrop && "z-20")}
                    item={item}
                    key={`left-menu-bottom-item-${leftMenuType}-${item.id}`}
                    indent={0}
                    openedAccordions={openedAccordions}
                    setOpenedAccordions={setOpenedAccordions}
                  />
                ),
              )}
          </Box>
        </Box>
      </Box>
      {leftMenuType !== MenuType.SingleLayer && (
        <Box
          className={cn(
            "shadow-line-left flex h-full shrink-0 grow-0 overflow-x-hidden transition-all duration-(--layout-duration)",
            leftShowBackdrop && "z-20",
          )}
          style={{
            width:
              activeItem?.children &&
              activeItem?.children.filter((x) => !x.hideInMenu).length > 0 &&
              leftSecondaryCurrent !== MenuShowState.Hide &&
              leftMenuWidth.secondary > 0
                ? `calc(${leftMenuWidth.secondary}px`
                : 0,
          }}
        >
          <Box className="h-full w-full">
            <Paper elevation={0} className="outline-line h-full w-full rounded-4xl py-8 outline -outline-offset-1">
              <Box className="relative h-full w-full overflow-x-hidden">
                <Box
                  style={{ width: leftSecondaryDefaultWidth }}
                  className={cn(
                    "absolute flex h-full min-h-full flex-col gap-2 overflow-y-scroll pr-[1rem] pl-[1.375rem]",
                  )}
                >
                  {activeItem?.label && (
                    <Typography variant="h6" className={"text-primary mb-4 px-2.5"}>
                      {t(activeItem?.label)}
                    </Typography>
                  )}
                  <Box className="flex h-full w-full flex-1 flex-col justify-between gap-2">
                    <Box className="flex flex-1 flex-col gap-2">
                      {activeItem?.children &&
                        activeItem?.children?.filter((x) => !x.hideInMenu).length > 0 &&
                        activeItem?.children
                          ?.filter((x) => !x.hideInMenu)
                          .map((item) => (
                            <SecondaryItem
                              item={item}
                              key={`left-menu-secondary-item-${leftMenuType}-${activeItem.id}-${item.id}`}
                              indent={0}
                              openedAccordions={openedAccordions}
                              setOpenedAccordions={setOpenedAccordions}
                            />
                          ))}
                    </Box>

                    <Box
                      component="a"
                      href="#"
                      className="group flex w-full cursor-pointer flex-col items-center justify-center gap-2"
                    >
                      <IllustrationLaunch className="text-primary h-[180px] w-[180px] bg-cover bg-center" />
                      <Typography variant="body1" className="px-4 text-center">
                        {t("menu-cta-copy")}
                      </Typography>
                      <Box className="group-hover:bg-primary/10 text-primary rounded-md px-5 py-2 font-medium transition-colors">
                        {t("menu-cta-button")}
                      </Box>
                    </Box>
                  </Box>
                </Box>
              </Box>
            </Paper>
          </Box>
        </Box>
      )}
    </nav>
  );
}
