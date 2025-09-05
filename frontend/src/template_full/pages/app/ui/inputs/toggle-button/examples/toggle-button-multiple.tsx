import { MouseEvent, useState } from "react";

import { Box, Card, CardContent, Grid, ToggleButton, ToggleButtonGroup, Typography } from "@mui/material";

import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiTextBold from "@/template_full/icons/nexture/ni-text-bold";
import NiTextFont from "@/template_full/icons/nexture/ni-text-font";
import NiTextItalic from "@/template_full/icons/nexture/ni-text-italic";
import NiTextUnderline from "@/template_full/icons/nexture/ni-text-underline";

export default function ToggleButtonMultiple() {
  const [formats, setFormats] = useState(() => ["bold", "italic"]);
  const handleFormat = (_event: MouseEvent<HTMLElement>, newFormats: string[]) => {
    setFormats(newFormats);
  };

  return (
    <Grid size={12}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h5" className="card-title">
            Multiple Selection
          </Typography>
          <Box className="border-grey-200 inline-flex rounded-2xl border border-solid p-1.75">
            <ToggleButtonGroup value={formats} onChange={handleFormat} size="small">
              <ToggleButton value="bold">
                <NiTextBold size="small" />
              </ToggleButton>
              <ToggleButton value="underlined">
                <NiTextUnderline size="small" />
              </ToggleButton>
              <ToggleButton value="italic">
                <NiTextItalic size="small" />
              </ToggleButton>
              <ToggleButton value="color" disabled>
                <NiTextFont size="small" />
                <NiChevronDownSmall size="small" />
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
}

