import { SyntheticEvent, useState } from "react";

import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";

import NiDrop from "@/icons/nexture/ni-drop";
import NiFire from "@/icons/nexture/ni-fire";
import NiFlash from "@/icons/nexture/ni-flash";

export default function TabsIcons() {
  const [value, setValue] = useState(0);

  const handleChange = (_event: SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Tabs value={value} onChange={handleChange} className="mb-2">
      <Tab icon={<NiFire size="medium" />} />
      <Tab icon={<NiDrop size="medium" />} />
      <Tab icon={<NiFlash size="medium" />} />
    </Tabs>
  );
}
