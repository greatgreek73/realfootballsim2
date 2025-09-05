import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { leftMenuBottomItems, leftMenuItems } from "@/template_full/menu-items";
import AppLayout from "@/template_full/pages/app/layout";
import AuthLayout from "@/template_full/pages/auth/layout";
import Loading from "@/template_full/pages/loading.tsx";
import NotFound from "@/template_full/pages/not-found";
import { MenuItem } from "@/template_full/types/types";

// Statically import all possible pages for build
const modules = import.meta.glob("./pages/**/page.tsx");

// Lazy load page components
const lazyLoad = (path: string) => {
  // Handle different paths based on the route
  let key: string;
  if (path === "/") {
    key = "./pages/page.tsx";
  } else if (path.startsWith("/auth")) {
    key = `./pages/auth${path.substring(5)}/page.tsx`; // Remove "/auth"
  } else {
    key = `./pages/app${path}/page.tsx`;
  }

  const importer = modules[key];

  // If file not found fallback to 404
  if (!importer) return <Navigate to="/404" replace />;

  const Component = React.lazy(importer as () => Promise<{ default: React.ComponentType<any> }>);

  return (
    <React.Suspense fallback={<Loading />}>
      <Component />
    </React.Suspense>
  );
};

// Recursively generate routes from menu items
const generateRoutesFromMenuItems = (menuItems: MenuItem[]): React.ReactElement[] => {
  return menuItems.flatMap((item: MenuItem) => {
    const routes: React.ReactElement[] = [];

    // Skip external links
    if (item.isExternalLink || !item.href) {
      return [];
    }

    // Add route for current item
    routes.push(<Route key={item.id} path={item.href} element={lazyLoad(item.href)} />);

    // Add routes for children
    if (item.children && item.children.length > 0) {
      routes.push(...generateRoutesFromMenuItems(item.children));
    }

    return routes;
  });
};

// Generate auth routes
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

// Generate routes from both menu arrays
const mainRoutes = generateRoutesFromMenuItems(leftMenuItems);
const bottomRoutes = generateRoutesFromMenuItems(leftMenuBottomItems);
const authRoutes = generateAuthRoutes();

// Main Routes component
const AppRoutes = () => {
  return (
    <Routes>
      {/* Landing page route */}

      <Route path="/" element={lazyLoad("/")} />

      {/* App routes with AppLayout */}
      <Route element={<AppLayout />}>
        {/* Routes generated from menu items */}
        {mainRoutes}
        {bottomRoutes}
      </Route>

      {/* Auth routes with AuthLayout */}
      <Route path="/auth" element={<AuthLayout />}>
        <Route index element={<Navigate to="/auth/sign-in" replace />} />
        {authRoutes}
      </Route>

      {/* 404 route */}
      <Route path="/404" element={<NotFound />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};

export default AppRoutes;

