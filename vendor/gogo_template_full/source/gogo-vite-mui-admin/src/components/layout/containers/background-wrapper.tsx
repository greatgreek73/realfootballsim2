import { useEffect, useState } from "react";

import { Box } from "@mui/material";

export default function BackgroundWrapper() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return <Box className={`bg-background fixed inset-0 -z-10 h-full w-full bg-cover`} />;
}
