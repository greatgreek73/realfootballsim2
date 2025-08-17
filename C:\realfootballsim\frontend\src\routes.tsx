import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { leftMenuBottomItems, leftMenuItems } from "@/menu-items";
import AppLayout from "@/pages/app/layout";
import AuthLayout from "@/pages/auth/layout";
import Loading from "@/pages/loading.tsx";
import NotFound from "@/pages/not-found";
import { MenuItem } from "@/types/types";

// Statically import all possible pages for build
const modules = import.meta.glob("./pages/**/page.tsx");

// Lazy load page components
const lazyLoad = (path: string) => {
  let key: string;
  if (path === "/") {
    key = "./pages/page.tsx";
  } else if (path.startsWith("/auth")) {
    key = `./pages/auth${path.substring(5)}/page.tsx`;
  } else {
    key = `./pages/app${path}/page.tsx`; // <-- ключ к страницам приложения
  }
  const importer = modules[key];
  if (!importer) return <Navigate to="/404" replace />; // если файла нет, отправляем на 404
  const Component = React.lazy(importer as () => Promise<{ default: React.ComponentType<any> }>);
  return (
    <React.Suspense fallback={<Loading />}>
      <Component />
    </React.Suspense>
  );
};

// Генерация маршрутов из меню
const generateRoutesFromMenuItems = (menuItems: MenuItem[]): React.ReactElement[] => {
  return menuItems.flatMap((item: MenuItem) => {
    const routes: React.ReactElement[] = [];
    if (item.isExternalLink || !item.href) return [];
    routes.push(<Route key={item.id} path={item.href} element={lazyLoad(item.href)} />);
    if (item.children && item.children.length > 0) {
      routes.push(...generateRoutesFromMenuItems(item.children));
    }
    return routes;
  });
};

// Auth-маршруты (ЗДЕСЬ НЕТ /my-club!)
const generateAuthRoutes = (): React.ReactElement[] => {
  return [
    <Route key="sign-in" path="sign-in" element={lazyLoad("/auth/sign-in")} />,
    <Route key="sign-up" path="sign-up" element={lazyLoad("/auth/sign-up")} />,
    <Route key="password-reset" path="password-reset" element={lazyLoad("/auth/password-reset")} />,
    <Route key="password-sent" path="password-sent" element={lazyLoad("/auth/password-sent")} />,
    <Route key="password-new" path="password-new" element={lazyLoad("/auth/password-new")} />,
    <Route key="get-verification" path="get-verification" element={lazyLoad("/auth/get-verification")} />,
    <Route key="set-verification" path="set-verification" element={lazyLoad("/auth/set-verification")} />,
  ];
};

const mainRoutes = generateRoutesFromMenuItems(leftMenuItems);
const bottomRoutes = generateRoutesFromMenuItems(leftMenuBottomItems);
const authRoutes = generateAuthRoutes();

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={lazyLoad("/")} />
      <Route element={<AppLayout />}>
        <Route key="my-club" path="/my-club" element={lazyLoad("/my-club")} />
        {mainRoutes}
        {bottomRoutes}
      </Route>
      <Route path="/auth" element={<AuthLayout />}>
        <Route index element={<Navigate to="/auth/sign-in" replace />} />
        {authRoutes}
      </Route>
      <Route path="/404" element={<NotFound />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};

export default AppRoutes;