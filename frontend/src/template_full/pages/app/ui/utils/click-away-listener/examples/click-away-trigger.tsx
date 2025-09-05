import { useState } from "react";

import { Box, Button, ClickAwayListener } from "@mui/material";

export default function ClickAwayTrigger() {
  const [open, setOpen] = useState(false);

  const handleClick = () => {
    setOpen((prev) => !prev);
  };

  const handleClickAway = () => {
    setOpen(false);
  };

  return (
    <ClickAwayListener onClickAway={handleClickAway} mouseEvent="onMouseDown" touchEvent="onTouchStart">
      <Box className="relative flex flex-row items-start gap-2">
        <Button onClick={handleClick} variant="pastel">
          Open Menu Dropdown
        </Button>
        {open ? (
          <Box className="bg-grey-25 top-0 rounded-md px-4 py-2 leading-5">
            Click me, I will close on mouse down and before the click.
          </Box>
        ) : null}
      </Box>
    </ClickAwayListener>
  );
}

