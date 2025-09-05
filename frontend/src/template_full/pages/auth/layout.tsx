import { Suspense } from "react";
import { Outlet } from "react-router-dom";

import Loading from "@/template_full/pages/loading";

export default function AuthLayout() {
  return (
    <Suspense fallback={<Loading />}>
      <Outlet />
    </Suspense>
  );
}

