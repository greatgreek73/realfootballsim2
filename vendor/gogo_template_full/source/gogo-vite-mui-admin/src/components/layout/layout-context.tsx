import { createContext, type PropsWithChildren, useContext, useEffect, useState } from "react";

import { DEFAULTS } from "@/config";
import { LOCAL_STORAGE_KEYS } from "@/constants";
import { useMenu } from "@/hooks/use-menu";
import { MenuShowState } from "@/types/types";

type LayoutContextType = ReturnType<typeof useLayoutContextValue>;

const LayoutContext = createContext<LayoutContextType | null>(null);

function useLayoutContextValue() {
  const [mounted, setMounted] = useState(false);

  const leftMenu = useMenu({
    primaryBreakpoint: "md",
    secondaryBreakpoint: "xl",
    storageKey: LOCAL_STORAGE_KEYS.leftMenuType,
    defaultMenuType: DEFAULTS.leftMenuType,
    menuDefaultWidth: DEFAULTS.leftMenuWidth,
  });

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Return initial state during SSR
  if (!mounted) {
    return {
      // Left menu
      leftMenuType: DEFAULTS.leftMenuType,
      setLeftMenuType: () => {},
      resetLeftMenu: () => {},
      showLeftMobileButton: false,
      leftMenuWidth: DEFAULTS.leftMenuWidth[DEFAULTS.leftMenuType],
      leftPrimaryCurrent: MenuShowState.Hide,
      leftSecondaryCurrent: MenuShowState.Hide,
      hideLeft: () => {},
      showLeftSecondary: () => {},
      hideLeftSecondary: () => {},
      showLeftInMobile: () => {},
      onResetLeft: () => () => {},
      leftShowBackdrop: false,
      setLeftShowBackdrop: () => {},
    };
  }

  return {
    // Left menu
    leftMenuType: leftMenu.menuType,
    setLeftMenuType: leftMenu.setMenuType,
    resetLeftMenu: leftMenu.resetMenu,
    showLeftMobileButton: leftMenu.showMobileButton,
    leftMenuWidth: leftMenu.menuWidth,
    leftPrimaryCurrent: leftMenu.primaryCurrent,
    leftSecondaryCurrent: leftMenu.secondaryCurrent,
    hideLeft: leftMenu.hideMenu,
    showLeftSecondary: leftMenu.showSecondary,
    hideLeftSecondary: leftMenu.hideSecondary,
    showLeftInMobile: leftMenu.showInMobile,
    onResetLeft: leftMenu.onReset,
    leftShowBackdrop: leftMenu.showBackdrop,
    setLeftShowBackdrop: leftMenu.setShowBackdrop,
  };
}

export default function LayoutContextProvider({ children }: PropsWithChildren) {
  const value = useLayoutContextValue();
  return <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>;
}

export const useLayoutContext = () => {
  const context = useContext(LayoutContext);
  if (!context) {
    throw new Error("useLayout must be used within a LayoutProvider");
  }
  return context;
};
