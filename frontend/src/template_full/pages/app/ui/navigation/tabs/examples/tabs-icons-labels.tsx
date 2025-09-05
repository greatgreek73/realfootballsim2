import { SyntheticEvent, useState } from "react";

import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";

import NiDrop from "@/template_full/icons/nexture/ni-drop";
import NiFire from "@/template_full/icons/nexture/ni-fire";
import NiFlash from "@/template_full/icons/nexture/ni-flash";

export default function TabsIconsLabels() {
  const [value, setValue] = useState(0);

  const handleChange = (_event: SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Tabs value={value} onChange={handleChange} className="mb-0">
      <Tab icon={<NiFire size="medium" />} iconPosition="start" label="Label 1" />
      <Tab icon={<NiDrop size="medium" />} iconPosition="start" label="Label 2" />
      <Tab icon={<NiFlash size="medium" />} iconPosition="start" label="Label 3" />
    </Tabs>
  );
}

