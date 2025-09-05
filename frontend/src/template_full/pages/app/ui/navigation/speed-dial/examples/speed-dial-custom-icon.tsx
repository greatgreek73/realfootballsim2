import Box from "@mui/material/Box";
import SpeedDial from "@mui/material/SpeedDial";
import SpeedDialAction from "@mui/material/SpeedDialAction";
import SpeedDialIcon from "@mui/material/SpeedDialIcon";

import NiCross from "@/icons/nexture/ni-cross";
import NiDuplicate from "@/icons/nexture/ni-duplicate";
import NiFloppyDisk from "@/icons/nexture/ni-floppy-disk";
import NiPenSquare from "@/icons/nexture/ni-pen-square";
import NiPrinter from "@/icons/nexture/ni-printer";
import NiShare from "@/icons/nexture/ni-share";

const actions = [
  { icon: <NiDuplicate />, name: "Copy" },
  { icon: <NiFloppyDisk />, name: "Save" },
  { icon: <NiPrinter />, name: "Print" },
  { icon: <NiShare />, name: "Share" },
];

export default function SpeedDialCustomIcon() {
  return (
    <Box className="h-60 grow translate-z-0 transform">
      <SpeedDial
        ariaLabel="SpeedDial openIcon example"
        className="absolute"
        icon={<SpeedDialIcon openIcon={<NiCross size="large" />} icon={<NiPenSquare size="large" />} />}
      >
        {actions.map((action) => (
          <SpeedDialAction key={action.name} icon={action.icon} tooltipTitle={action.name} tooltipPlacement="right" />
        ))}
      </SpeedDial>
    </Box>
  );
}
