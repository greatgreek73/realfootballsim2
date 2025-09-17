import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function DocsTheme() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/docs/theme/settings");
  }, [navigate]);
  return <></>;
}
