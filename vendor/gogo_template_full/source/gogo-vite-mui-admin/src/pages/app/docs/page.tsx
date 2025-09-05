import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Docs() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/docs/welcome/introduction");
  }, [navigate]);
  return <></>;
}
