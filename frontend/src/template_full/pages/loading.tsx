import { Box, CircularProgress } from "@mui/material";

export default function Loading() {
  return (
    <Box className="fixed top-0 right-0 bottom-0 left-0 z-[9999] flex flex-col items-center justify-center">
      <CircularProgress color="primary" size={32} />
    </Box>
  );
}
