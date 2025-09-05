import { SyntheticEvent, useState } from "react";

import Box from "@mui/material/Box";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";

import NiChevronLeftSmall from "@/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";

export default function TabsScrollable() {
  const [value, setValue] = useState(0);

  const handleChange = (_event: SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box className="max-w-sm">
      <Tabs
        value={value}
        onChange={handleChange}
        variant="scrollable"
        allowScrollButtonsMobile
        slots={{
          EndScrollButtonIcon: () => {
            return <NiChevronRightSmall size="medium" />;
          },
          StartScrollButtonIcon: () => {
            return <NiChevronLeftSmall size="medium" />;
          },
        }}
      >
        <Tab label="Item One" />
        <Tab label="Item Two" />
        <Tab label="Item Three" />
        <Tab label="Item Four" />
        <Tab label="Item Five" />
        <Tab label="Item Six" />
        <Tab label="Item Seven" />
      </Tabs>
    </Box>
  );
}
