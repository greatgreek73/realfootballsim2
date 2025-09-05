import Footer from "./footer";
import { PropsWithChildren, useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

import { useLayoutContext } from "@/components/layout/layout-context";
import { isPathMatch } from "@/lib/utils";
import { leftMenuBottomItems } from "@/menu-items";
import { leftMenuItems } from "@/menu-items";
import { MenuItem, MenuShowState } from "@/types/types";

export default function Main({ children }: PropsWithChildren) {
  const { leftPrimaryCurrent, leftSecondaryCurrent, leftMenuWidth } = useLayoutContext();
  const [mounted, setMounted] = useState(false);
  const { pathname } = useLocation();

  useEffect(() => {
    setMounted(true);
  }, []);

  const [activeItem, setActiveItem] = useState<MenuItem | undefined>(undefined);

  useEffect(() => {
    let selectedMenu = leftMenuItems.find((item) => item.href && isPathMatch(pathname, item.href));
    if (!selectedMenu && leftMenuBottomItems) {
      selectedMenu = leftMenuBottomItems.find((item) => item.href && isPathMatch(pathname, item.href));
    }
    setActiveItem(selectedMenu);
  }, [pathname]);

  const [mainPaddingLeft] = useMemo(() => {
    if (!mounted) return [0];

    let mainPaddingLeft = 0;

    if (leftPrimaryCurrent === MenuShowState.Show) {
      mainPaddingLeft += leftMenuWidth.primary;
    }
    if (
      leftSecondaryCurrent === MenuShowState.Show &&
      activeItem?.children &&
      activeItem?.children.filter((x) => !x.hideInMenu).length > 0 &&
      leftMenuWidth.secondary > 0
    ) {
      mainPaddingLeft += leftMenuWidth.secondary;
    }

    return [mainPaddingLeft];
  }, [leftPrimaryCurrent, leftSecondaryCurrent, leftMenuWidth, mounted, activeItem]);

  const styles = useMemo(
    () => ({
      width: "100%",
      paddingLeft: `calc(${mainPaddingLeft}px`,
    }),
    [mainPaddingLeft],
  );

  return (
    <main className="flex h-full min-h-0 w-full flex-col pt-20 duration-(--layout-duration)" style={styles}>
      {children}
      <Footer />
    </main>
  );
}
