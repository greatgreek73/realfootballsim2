import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { DEFAULTS } from "@/config";
import { getJSON } from "@/lib/apiClient";

export default function Page() {
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const me = await getJSON("/api/auth/me/");
        if (me?.authenticated) {
          navigate(DEFAULTS.appRoot, { replace: true });
        } else {
          navigate("/auth/sign-in", { replace: true });
        }
      } catch {
        navigate("/auth/sign-in", { replace: true });
      }
    })();
  }, [navigate]);

  return null;
}
