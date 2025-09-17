import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function DocsGettingStarted() {
  const navigate = useNavigate();
  useEffect(() => {
    navigate("/docs/getting-started/installation");
  }, [navigate]);
  return <></>;
}
