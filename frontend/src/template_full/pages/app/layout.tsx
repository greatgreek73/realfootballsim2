import "@/template_full/style/global.css";

import { Suspense, useEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";

import ContentWrapper from "@/template_full/components/layout/containers/content-wrapper";
import Header from "@/template_full/components/layout/containers/header";
import Main from "@/template_full/components/layout/containers/main";
import ThemeConfiguration from "@/template_full/components/layout/containers/theme-configuration";
import LeftMenu from "@/template_full/components/layout/menu/left-menu";
import MenuBackdrop from "@/template_full/components/layout/menu/menu-backdrop";
import Loading from "@/template_full/pages/loading";

export default function AppLayout() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <>
      <Header />
      <LeftMenu />
      <Main>
        <ContentWrapper>
          <Suspense fallback={<Loading />}>
            <Outlet />
          </Suspense>
        </ContentWrapper>
      </Main>
      <ThemeConfiguration />
      <MenuBackdrop />
    </>
  );
}

