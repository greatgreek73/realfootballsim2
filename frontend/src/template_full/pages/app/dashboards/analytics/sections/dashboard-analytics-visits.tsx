import { useMemo, useState } from "react";

import { Box, Button, Card, CardContent, Typography, useTheme } from "@mui/material";
import { LineChart, LineSeriesType } from "@mui/x-charts";

import CustomChartTooltip from "@/template_full/components/charts/tooltip/custom-chart-tooltip";
import NiBookmark from "@/template_full/icons/nexture/ni-bookmark";
import NiController from "@/template_full/icons/nexture/ni-controller";
import NiRocket from "@/template_full/icons/nexture/ni-rocket";
import NiStructure from "@/template_full/icons/nexture/ni-structure";
import { colorWithOpacity } from "@/template_full/lib/chart-helper";

export default function DashboardAnalyticsVisits() {
  const { palette } = useTheme();
  const [activeIndex, setActiveIndex] = useState<number>(0);

  const series = useMemo(() => {
    const books: Omit<LineSeriesType, "type"> = {
      data: [280, 340, 310, 355, 295, 320, 305],
      label: "Books",
      stack: "all",
      area: true,
      showMark: false,
      color: palette["accent-1"].main,
      curve: "bumpX",
    };
    const toys: Omit<LineSeriesType, "type"> = {
      data: [180, 230, 170, 220, 185, 210, 190],
      label: "Toys",
      stack: "all",
      area: true,
      showMark: false,
      color: palette.secondary.main,
      curve: "bumpX",
    };
    const games: Omit<LineSeriesType, "type"> = {
      data: [80, 120, 95, 130, 90, 115, 85],
      label: "Games",
      stack: "all",
      area: true,
      showMark: false,
      color: palette["accent-3"].main,
      curve: "bumpX",
    };

    switch (activeIndex) {
      case 1:
        return [books];
      case 2:
        return [toys];
      case 3:
        return [games];
      case 0:
      default:
        return [books, toys, games];
    }
  }, [activeIndex, palette]);

  return (
    <Card className="h-96">
      <CardContent>
        <Typography variant="h5" component="h5" className="card-title">
          Visits
        </Typography>

        <Box className="mb-1 flex gap-1">
          <Button
            variant="outlined"
            size="medium"
            startIcon={<NiStructure size="medium" />}
            color={activeIndex === 0 ? "primary" : "grey"}
            onClick={() => setActiveIndex(0)}
          >
            All
          </Button>
          <Button
            variant="outlined"
            size="medium"
            startIcon={<NiBookmark size="medium" />}
            color={activeIndex === 1 ? "primary" : "grey"}
            onClick={() => setActiveIndex(1)}
          >
            Books
          </Button>
          <Button
            variant="outlined"
            size="medium"
            startIcon={<NiRocket size="medium" />}
            color={activeIndex === 2 ? "primary" : "grey"}
            onClick={() => setActiveIndex(2)}
          >
            Toys
          </Button>
          <Button
            variant="outlined"
            size="medium"
            startIcon={<NiController size="medium" />}
            color={activeIndex === 3 ? "primary" : "grey"}
            onClick={() => setActiveIndex(3)}
          >
            Games
          </Button>
        </Box>

        <LineChart
          series={series}
          xAxis={[
            {
              disableLine: true,
              disableTicks: true,
              data: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              scaleType: "band",
            },
          ]}
          yAxis={[{ disableLine: true, disableTicks: true, width: 30 }]}
          slots={{ tooltip: CustomChartTooltip }}
          slotProps={{ area: ({ color }) => ({ fill: colorWithOpacity(color) }) }}
          height={250}
          hideLegend
          grid={{ horizontal: true }}
          margin={{ bottom: 0, left: 0, right: 0 }}
        />
      </CardContent>
    </Card>
  );
}

