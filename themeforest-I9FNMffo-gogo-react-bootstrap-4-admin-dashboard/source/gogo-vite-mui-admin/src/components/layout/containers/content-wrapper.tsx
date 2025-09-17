import { PropsWithChildren, useEffect, useState } from "react";

import { Box, Paper } from "@mui/material";

import { cn } from "@/lib/utils";
import { useThemeContext } from "@/theme/theme-provider";
import { ContentType } from "@/types/types";

export default function ContentWrapper({ children }: PropsWithChildren) {
  const { content } = useThemeContext();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <Paper
      elevation={0}
      className="flex min-h-[calc(100vh-7.5rem)] w-full min-w-0 rounded-xl bg-transparent px-4 py-5 sm:rounded-4xl sm:py-6 md:py-8 lg:px-12"
    >
      <Box className="flex w-full">
        <Box className={cn("mx-auto w-full transition-all", content === ContentType.Boxed && "max-w-screen-2xl")}>
          <Box className="-mx-2 min-h-full overflow-x-auto px-2 *:mb-2">{children}</Box>
        </Box>
      </Box>
    </Paper>
  );
}
