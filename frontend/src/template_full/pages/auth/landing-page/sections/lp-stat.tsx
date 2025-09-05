import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, Typography, useTheme } from "@mui/material";
import { SparkLineChart } from "@mui/x-charts";

import useHighlightedSparkline from "@/template_full/hooks/use-highlighted-sparkline";
import NiTriangleDown from "@/template_full/icons/nexture/ni-triangle-down";
import NiTriangleUp from "@/template_full/icons/nexture/ni-triangle-up";

const earningsData = [60, 140, 140, 140, 220, 340, 340, 100, 60, 120, 340];

export default function LPStat() {
  const { t } = useTranslation();
  const { palette } = useTheme();

  const earningsSparkline = useHighlightedSparkline({
    data: earningsData,
    plotType: "line",
    color: palette.primary.main,
  });

  return (
    <Card className="w-[240px]">
      <CardContent className="flex flex-col gap-5">
        <Box className="flex flex-col">
          <Typography variant="body1" className="text-text-secondary">
            {t("landing-earnings")}
          </Typography>
          <Box className="flex flex-row items-center justify-start gap-2 lg:justify-between lg:gap-0">
            <Typography variant="h5" className="text-text-primary">
              ${earningsSparkline.item.value}
            </Typography>
            <ChangeStatus change={earningsSparkline.item.change} />
          </Box>
        </Box>

        <SparkLineChart {...earningsSparkline.props} />
      </CardContent>
    </Card>
  );
}

const ChangeStatus = ({ change }: { change: number | string }) => {
  return (
    <Box className="flex">
      {Number(change) < 0 ? (
        <NiTriangleDown size="tiny" className={"text-error"} />
      ) : (
        <NiTriangleUp size="tiny" className="text-success" />
      )}
      <Typography variant="body2" className={Number(change) < 0 ? "text-error" : "text-success"}>
        {Math.abs(Number(change))}%
      </Typography>
    </Box>
  );
};

