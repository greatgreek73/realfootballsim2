import { BarChart, BarElement } from "@mui/x-charts";

import CustomChartTooltip from "@/components/charts/tooltip/custom-chart-tooltip";
import useChartPalette from "@/hooks/use-chart-palette";
import { withChartElementStyle } from "@/lib/chart-element-hoc";

export default function BasicBar() {
  const chartPalette = useChartPalette();

  return (
    <BarChart
      series={[{ data: [4, 3, 5] }, { data: [1, 6, 3] }, { data: [2, 5, 6] }]}
      xAxis={[
        {
          data: ["group A", "group B", "group C"],
          categoryGapRatio: 0.5,
          barGapRatio: 0.2,
          disableLine: true,
          disableTicks: true,
        },
      ]}
      yAxis={[{ domainLimit: (min, max) => ({ min, max: max + 0.1 }), disableLine: true, disableTicks: true }]}
      height={300}
      slots={{ tooltip: CustomChartTooltip, bar: withChartElementStyle(BarElement, { rx: 5, ry: 5 }) }}
      grid={{ horizontal: true }}
      {...chartPalette}
    />
  );
}
