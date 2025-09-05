import { SyntheticEvent, useState } from "react";

import { Box, Button, Fade, Menu, MenuItem, PopoverVirtualElement } from "@mui/material";

import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import { cn } from "@/template_full/lib/utils";

export default function MenuOutlined() {
  const [anchorElOutlined, setAnchorElOutlined] = useState<EventTarget | Element | PopoverVirtualElement | null>(null);
  const openOutlined = Boolean(anchorElOutlined);
  const handleClickOutlined = (event: Event | SyntheticEvent) => {
    setAnchorElOutlined(event.currentTarget);
  };
  const handleCloseOutlined = () => {
    setAnchorElOutlined(null);
  };

  return (
    <Box>
      <Button
        variant="outlined"
        onClick={handleClickOutlined}
        endIcon={
          <NiChevronRightSmall size="medium" className={cn("transition-transform", openOutlined && "rotate-90")} />
        }
      >
        Outlined
      </Button>
      <Menu
        anchorEl={anchorElOutlined as Element}
        open={openOutlined}
        onClose={handleCloseOutlined}
        className="outlined mt-1"
        slots={{
          transition: Fade,
        }}
      >
        <MenuItem onClick={handleCloseOutlined}>Profile</MenuItem>
        <MenuItem onClick={handleCloseOutlined}>Account</MenuItem>
        <MenuItem onClick={handleCloseOutlined}>New Account</MenuItem>
        <MenuItem onClick={handleCloseOutlined}>Logout</MenuItem>
      </Menu>
    </Box>
  );
}

