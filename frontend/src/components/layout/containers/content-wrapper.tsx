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
      className="flex min-h-[calc(100vh-7.5rem)] w-full min-w-0 rounded-xl bg-transparent px-4 pt-3 pb-5 sm:rounded-4xl sm:pt-4 sm:pb-6 md:pt-5 md:pb-8 lg:px-12"
    >
      <Box className="flex w-full">
        <Box className="mx-auto flex min-h-full w-full flex-col transition-all">
          <Box className="-mx-2 flex min-h-full flex-col px-2 *:mb-2 flex-1">{children}</Box>
        </Box>
      </Box>
    </Paper>
  );
}
