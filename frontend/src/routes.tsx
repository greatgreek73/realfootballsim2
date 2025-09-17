import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { leftMenuBottomItems, leftMenuItems } from "@/menu-items";
import DemoRouter from "@/router/DemoRouter";
import AppLayout from "@/pages/app/layout";
import AuthLayout from "@/pages/auth/layout";
import Loading from "@/pages/loading.tsx";
import NotFound from "@/pages/not-found";
import { MenuItem } from "@/types/types";

// Сканируем все page.tsx
const modules = import.meta.glob("./pages/**/page.tsx");

// Ленивый загрузчик (для ваших страниц)
const lazyLoad = (path: string) => {
  let key: string;
  if (path === "/") {
    key = "./pages/page.tsx";
  } else if (path.startsWith("/auth")) {
    key = `./pages/auth${path.substring(5)}/page.tsx`;
  } else {
    key = `./pages/app${path}/page.tsx`;
  }
  const importer = modules[key];
  if (!importer) return <Navigate to="/404" replace />;
  const Component = React.lazy(
    importer as () => Promise<{ default: React.ComponentType<any> }>
  );
  return (
    <React.Suspense fallback={<Loading />}>
      <Component />
    </React.Suspense>
  );
};

// Пути демо, которые должен обрабатывать DemoRouter
const DEMO_PREFIXES = ["/dashboards/", "/ui/", "/apps/", "/forms/", "/tables/", "/charts/", "/docs/"];

const generateRoutesFromMenuItems = (menuItems: MenuItem[]): React.ReactElement[] =>
  menuItems.flatMap((item: MenuItem) => {
    if (item.isExternalLink || !item.href) return [];
    // Демо-пути НЕ генерируем через lazyLoad – их отдаст DemoRouter
    if (DEMO_PREFIXES.some((p) => item.href!.startsWith(p))) {
      return item.children?.length ? generateRoutesFromMenuItems(item.children) : [];
    }
    const routes: React.ReactElement[] = [
      <Route key={item.id} path={item.href} element={lazyLoad(item.href)} />,
    ];
    if (item.children?.length) routes.push(...generateRoutesFromMenuItems(item.children));
    return routes;
  });

const generateAuthRoutes = (): React.ReactElement[] => [
  <Route key="sign-in" path="sign-in" element={lazyLoad("/auth/sign-in")} />,
  <Route key="sign-up" path="sign-up" element={lazyLoad("/auth/sign-up")} />,
  <Route key="password-reset" path="password-reset" element={lazyLoad("/auth/password-reset")} />,
  <Route key="password-sent" path="password-sent" element={lazyLoad("/auth/password-sent")} />,
  <Route key="password-new" path="password-new" element={lazyLoad("/auth/password-new")} />,
  <Route key="get-verification" path="get-verification" element={lazyLoad("/auth/get-verification")} />,
  <Route key="set-verification" path="set-verification" element={lazyLoad("/auth/set-verification")} />,
];

const mainRoutes = generateRoutesFromMenuItems(leftMenuItems);
const bottomRoutes = generateRoutesFromMenuItems(leftMenuBottomItems);
const authRoutes = generateAuthRoutes();

const AppRoutes = () => (
  <Routes>
    {/* Корень остаётся на ваш интерфейс */}
    <Route path="/" element={<Navigate to="/my-club" replace />} />

    {/* Зона приложения */}
    <Route element={<AppLayout />}>
      {/* Ваши основные страницы */}
      <Route key="my-club" path="/my-club" element={lazyLoad("/my-club")} />
      <Route key="my-club-players" path="/my-club/players" element={lazyLoad("/my-club/players")} />

      {/* Автогенерация маршрутов из вашего меню (кроме демо) */}
      {mainRoutes}
      {bottomRoutes}

      {/* Демо-страницы шаблона — через динамический DemoRouter */}
      <Route path="/dashboards/*" element={<DemoRouter />} />
      <Route path="/ui/*"         element={<DemoRouter />} />
      <Route path="/apps/*"       element={<DemoRouter />} />
      <Route path="/forms/*"      element={<DemoRouter />} />
      <Route path="/tables/*"     element={<DemoRouter />} />
      <Route path="/charts/*"     element={<DemoRouter />} />
      <Route path="/docs/*"       element={<DemoRouter />} />
    </Route>

    {/* Auth */}
    <Route path="/auth" element={<AuthLayout />}>
      <Route index element={<Navigate to="/auth/sign-in" replace />} />
      {authRoutes}
    </Route>

    <Route path="/404" element={<NotFound />} />
    <Route path="*" element={<Navigate to="/404" replace />} />
  </Routes>
);

export default AppRoutes;
