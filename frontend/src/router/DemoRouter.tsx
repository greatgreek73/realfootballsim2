import React, { Suspense } from "react";
import { Navigate, useLocation } from "react-router-dom";

const modules = import.meta.glob("../pages/**/page.tsx");

function normalize(pathname: string): string {
  return pathname.replace(/^\/+/, "").replace(/\/+$/, "");
}

function resolveKey(routePath: string) {
  const normalized = normalize(routePath);
  const candidates = [
    `../pages/app/${normalized}/page.tsx`,
    `../pages/${normalized}/page.tsx`,
  ];
  for (const key of candidates) {
    if (key in modules) return key;
  }

  const [section, ...rest] = normalized.split("/");
  const restPath = rest.join("/");
  if (section) {
    const demoKey = `../pages/demo_${section}/${restPath}/page.tsx`;
    if (demoKey in modules) return demoKey;
  }

  const keys = Object.keys(modules);
  const suffix = `/${normalized}/page.tsx`;
  const found =
    keys.find((k) => k.endsWith(suffix)) ||
    keys.find((k) => k.endsWith(`/app${suffix}`));
  return found;
}

export default function DemoRouter() {
  const location = useLocation();
  const pathname = normalize(location.pathname);
  const key = resolveKey(pathname);

  console.info('[DemoRouter]', pathname || '<index>', '->', key ?? '<not-found>');

  if (!key) return <Navigate to="/404" replace />;

  const Component = React.lazy(modules[key] as () => Promise<{ default: React.ComponentType<any> }>);

  return (
    <Suspense key={key} fallback={<div />}>
      <Component />
    </Suspense>
  );
}
