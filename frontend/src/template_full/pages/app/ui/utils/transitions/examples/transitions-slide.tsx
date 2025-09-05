import { useState } from "react";

import Box from "@mui/material/Box";
import FormControlLabel from "@mui/material/FormControlLabel";
import Paper from "@mui/material/Paper";
import Slide from "@mui/material/Slide";
import Switch from "@mui/material/Switch";

const icon = (
  <Paper className="border-grey-100 h-24 w-24 rounded-lg border p-4">
    <svg className="h-16 w-16">
      <Box component="polygon" points="0,60 30,00, 60,60" className="fill-grey-25" />
    </svg>
  </Paper>
);

export default function TransitionsSlide() {
  const [checked, setChecked] = useState(false);

  const handleChange = () => {
    setChecked((prev) => !prev);
  };

  return (
    <Box>
      <FormControlLabel control={<Switch checked={checked} onChange={handleChange} />} label="Show" className="mb-4" />
      <Box className="flex flex-col justify-between gap-2">
        <Box className="h-24 w-24">
          <Slide direction="right" in={checked} mountOnEnter unmountOnExit>
            {icon}
          </Slide>
        </Box>
        <Box className="h-24 w-24">
          <Slide direction="left" in={checked} mountOnEnter unmountOnExit>
            {icon}
          </Slide>
        </Box>
      </Box>
    </Box>
  );
}

