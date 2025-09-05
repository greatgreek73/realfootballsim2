import { useEffect, useState } from "react";

import { Box, CircularProgress, Typography } from "@mui/material";

export default function ProgressCircularLabel() {
  const [progress, setProgress] = useState(10);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prevProgress) => (prevProgress >= 100 ? 0 : prevProgress + 10));
    }, 800);
    return () => {
      clearInterval(timer);
    };
  }, []);

  return (
    <Box className="relative inline-flex">
      <CircularProgress variant="determinate" value={progress} className="h-10! w-10!" />
      <Box className="absolute top-0 right-0 bottom-0 left-0 flex items-center justify-center">
        <Typography
          variant="caption"
          component="div"
          className="text-text-secondary"
        >{`${Math.round(progress)}%`}</Typography>
      </Box>
    </Box>
  );
}
