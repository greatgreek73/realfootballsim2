import "@/style/global.css";

import { Suspense, useEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";

import ContentWrapper from "@/components/layout/containers/content-wrapper";
import Header from "@/components/layout/containers/header";
import Main from "@/components/layout/containers/main";
import LeftMenu from "@/components/layout/menu/left-menu";
import MenuBackdrop from "@/components/layout/menu/menu-backdrop";
import Loading from "@/pages/loading";

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
      <MenuBackdrop />
    </>
  );
}
