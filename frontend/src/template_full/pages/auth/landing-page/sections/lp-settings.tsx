import { Card, CardContent, MenuList } from "@mui/material";

import UserLanguageSwitch from "@/template_full/components/layout/user/user-language-switch";
import UserModeSwitch from "@/template_full/components/layout/user/user-mode-switch";
import UserThemeSwitch from "@/template_full/components/layout/user/user-theme-switch";

export default function LPSettings() {
  return (
    <Card className="w-[320px]">
      <CardContent className="p-0!">
        <MenuList className="p-0">
          <UserModeSwitch />
          <UserThemeSwitch />
          <UserLanguageSwitch />
        </MenuList>
      </CardContent>
    </Card>
  );
}

