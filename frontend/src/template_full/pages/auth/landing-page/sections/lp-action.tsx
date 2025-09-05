import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, Typography } from "@mui/material";

import NiBag from "@/template_full/icons/nexture/ni-bag";

export default function LPAction() {
  const { t } = useTranslation();

  return (
    <Card component="a" href="#" className="flex flex-row p-1 transition-transform hover:scale-[1.02]">
      <Box className="bg-accent-3-light/10 flex w-16 flex-none items-center justify-center rounded-2xl">
        <NiBag className="text-accent-3" size={"large"} />
      </Box>
      <CardContent className="flex w-full flex-row justify-between gap-4">
        <Box>
          <Typography variant="subtitle2" className="leading-5 transition-colors">
            {t("landing-track-metrics")}
          </Typography>
          <Typography variant="body1" className="text-text-secondary line-clamp-1 leading-5">
            {t("landing-track-metrics-desc")}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

