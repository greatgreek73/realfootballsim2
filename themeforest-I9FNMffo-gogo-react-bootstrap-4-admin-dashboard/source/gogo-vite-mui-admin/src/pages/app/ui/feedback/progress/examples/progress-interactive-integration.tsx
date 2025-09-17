import { useEffect, useRef, useState } from "react";

import { Box, Button, CircularProgress, Fab } from "@mui/material";

import NiCheck from "@/icons/nexture/ni-check";
import NiFloppyDisk from "@/icons/nexture/ni-floppy-disk";

export default function ProgressInteractiveIntegration() {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    return () => {
      clearTimeout(timer.current);
    };
  }, []);

  const handleButtonClick = () => {
    if (!loading) {
      setSuccess(false);
      setLoading(true);
      timer.current = setTimeout(() => {
        setSuccess(true);
        setLoading(false);
      }, 2000);
    }
  };

  const getIcon = () => {
    if (!loading) {
      if (success) {
        return <NiCheck />;
      } else {
        return <NiFloppyDisk />;
      }
    } else {
      return <NiFloppyDisk className="opacity-0" />;
    }
  };

  return (
    <Box className="flex items-center">
      <Box className="relative m-1">
        <Fab color="primary" disabled={loading} onClick={handleButtonClick}>
          {getIcon()}
        </Fab>
        {loading && <CircularProgress className="medium text-text-contrast absolute top-2 left-2 z-1051" />}
      </Box>
      <Box className="relative m-1">
        <Button variant="contained" className="w-40" disabled={loading} onClick={handleButtonClick}>
          {!success ? "Accept Terms" : "Terms Accepted!"}
        </Button>
        {loading && (
          <CircularProgress className="medium text-text-contrast absolute top-1/2 left-1/2 z-1051 -mt-2.5 -ml-2.5" />
        )}
      </Box>
    </Box>
  );
}
