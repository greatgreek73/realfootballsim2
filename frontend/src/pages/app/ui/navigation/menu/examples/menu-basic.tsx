import { SyntheticEvent, useState } from "react";

import { Box, Button, Fade, Menu, MenuItem, PopoverVirtualElement } from "@mui/material";

import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";
import { cn } from "@/lib/utils";

export default function MenuBasic() {
  const [anchorEl, setAnchorEl] = useState<EventTarget | Element | PopoverVirtualElement | null>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: Event | SyntheticEvent) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  return (
    <Box>
      <Button
        variant="outlined"
        color="grey"
        onClick={handleClick}
        endIcon={<NiChevronRightSmall size="medium" className={cn("transition-transform", open && "rotate-90")} />}
      >
        Basic
      </Button>
      <Menu
        anchorEl={anchorEl as Element}
        open={open}
        onClose={handleClose}
        className="mt-1"
        slots={{
          transition: Fade,
        }}
      >
        <MenuItem onClick={handleClose}>Profile</MenuItem>
        <MenuItem onClick={handleClose}>Account</MenuItem>
        <MenuItem onClick={handleClose}>New Account</MenuItem>
        <MenuItem onClick={handleClose}>Logout</MenuItem>
      </Menu>
    </Box>
  );
}
