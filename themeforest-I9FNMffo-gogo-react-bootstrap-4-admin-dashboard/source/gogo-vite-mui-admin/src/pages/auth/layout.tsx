import { Suspense } from "react";
import { Outlet } from "react-router-dom";

import Loading from "@/pages/loading";

export default function AuthLayout() {
  return (
    <Suspense fallback={<Loading />}>
      <Outlet />
    </Suspense>
  );
}
