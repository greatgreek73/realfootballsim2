import { SyntheticEvent, useState } from "react";

import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";

import NiDrop from "@/icons/nexture/ni-drop";
import NiFire from "@/icons/nexture/ni-fire";
import NiFlash from "@/icons/nexture/ni-flash";

export default function TabsIconsIconOnly() {
  const [value, setValue] = useState(0);

  const handleChange = (_event: SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Tabs value={value} onChange={handleChange} className="mb-2">
      <Tab icon={<NiFire size="medium" />} className="icon-only" />
      <Tab icon={<NiDrop size="medium" />} className="icon-only" />
      <Tab icon={<NiFlash size="medium" />} className="icon-only" />
    </Tabs>
  );
}
