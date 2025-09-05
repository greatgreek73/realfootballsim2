import { useState } from "react";

import Box from "@mui/material/Box";
import SpeedDial from "@mui/material/SpeedDial";
import SpeedDialAction from "@mui/material/SpeedDialAction";

import NiDuplicate from "@/template_full/icons/nexture/ni-duplicate";
import NiFloppyDisk from "@/template_full/icons/nexture/ni-floppy-disk";
import NiPlus from "@/template_full/icons/nexture/ni-plus";
import NiPrinter from "@/template_full/icons/nexture/ni-printer";
import NiShare from "@/template_full/icons/nexture/ni-share";

const actions = [
  { icon: <NiDuplicate />, name: "Copy" },
  { icon: <NiFloppyDisk />, name: "Save" },
  { icon: <NiPrinter />, name: "Print" },
  { icon: <NiShare />, name: "Share" },
];

export default function SpeedDialControlled() {
  const [open, setOpen] = useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  return (
    <Box className="h-60 grow translate-z-0 transform">
      <SpeedDial
        className="absolute"
        ariaLabel="SpeedDial"
        direction="down"
        icon={<NiPlus size="large" />}
        onClose={handleClose}
        onOpen={handleOpen}
        open={open}
      >
        {actions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={handleClose}
            tooltipPlacement="right"
          />
        ))}
      </SpeedDial>
    </Box>
  );
}

