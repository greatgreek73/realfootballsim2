import { SyntheticEvent, useState } from "react";

import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";

export default function TabsDisabled() {
  const [value, setValue] = useState(2);

  const handleChange = (_event: SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Tabs value={value} onChange={handleChange} className="mb-0">
      <Tab label="Active" />
      <Tab label="Disabled" disabled />
      <Tab label="Active" />
    </Tabs>
  );
}
