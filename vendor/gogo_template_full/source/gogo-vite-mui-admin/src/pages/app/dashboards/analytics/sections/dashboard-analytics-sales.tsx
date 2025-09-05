import { useMemo, useState } from "react";

import { Box, Button, Card, CardContent, Typography, useTheme } from "@mui/material";
import { BarChart, BarElement, BarSeriesType } from "@mui/x-charts";

import CustomChartTooltip from "@/components/charts/tooltip/custom-chart-tooltip";
import NiBookmark from "@/icons/nexture/ni-bookmark";
import NiController from "@/icons/nexture/ni-controller";
import NiRocket from "@/icons/nexture/ni-rocket";
import NiStructure from "@/icons/nexture/ni-structure";
import { withChartElementStyle } from "@/lib/chart-element-hoc";

export default function DashboardAnalyticsSales() {
  const { palette } = useTheme();
  const [activeIndex, setActiveIndex] = useState<number>(0);

  const series = useMemo(() => {
    const books: Omit<BarSeriesType, "type"> = {
      data: [280, 340, 310, 355, 295, 320, 305],
      label: "Books",
      stack: "all",
      color: palette.primary.main,
    };
    const toys: Omit<BarSeriesType, "type"> = {
      data: [180, 230, 170, 220, 185, 210, 190],
      label: "Toys",
      stack: "all",
      color: palette.secondary.main,
    };
    const games: Omit<BarSeriesType, "type"> = {
      data: [140, 120, 160, 130, 120, 115, 110],
      label: "Games",
      stack: "all",
      color: palette["accent-1"].main,
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
          Sales
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

        <BarChart
          series={series}
          xAxis={[
            {
              disableLine: true,
              disableTicks: true,
              data: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              scaleType: "band",
              categoryGapRatio: 0.5,
            },
          ]}
          yAxis={[{ disableLine: true, disableTicks: true, valueFormatter: (value: number) => `$${value}`, width: 40 }]}
          slots={{ tooltip: CustomChartTooltip, bar: withChartElementStyle(BarElement, { rx: 10, ry: 10 }) }}
          height={250}
          hideLegend
          grid={{ horizontal: true }}
          axisHighlight={{ x: "line" }}
          margin={{ bottom: 0, left: 0, right: 0 }}
        />
      </CardContent>
    </Card>
  );
}
