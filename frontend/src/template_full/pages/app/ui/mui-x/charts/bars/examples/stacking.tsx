import { BarChart, BarElement } from "@mui/x-charts";

import CustomChartTooltip from "@/template_full/components/charts/tooltip/custom-chart-tooltip";
import useChartPalette from "@/template_full/hooks/use-chart-palette";
import { withChartElementStyle } from "@/template_full/lib/chart-element-hoc";

export default function Stacking() {
  const chartPalette = useChartPalette();

  return (
    <BarChart
      dataset={[
        {
          year: "2020",
          currAss: 9761580,
          nCurrAss: 29518779,
          curLia: 7805785,
          nCurLia: 20409334,
          capStock: 3447698,
          retEarn: 7573144,
          treas: null,
        },
        {
          year: "2021",
          currAss: 8069825,
          nCurrAss: 36514838,
          curLia: 8488966,
          nCurLia: 20246449,
          capStock: 4024561,
          retEarn: 12689372,
          treas: 824190,
        },
        {
          year: "2022",
          currAss: 9266473,
          nCurrAss: 39328295,
          curLia: 7930974,
          nCurLia: 19886393,
          capStock: 4637601,
          retEarn: 17181296,
          treas: 824190,
        },
        {
          year: "2023",
          currAss: 9918133,
          nCurrAss: 38813859,
          curLia: 8860655,
          nCurLia: 19283024,
          capStock: 5145172,
          retEarn: 22589286,
          treas: 6922200,
        },
      ]}
      series={[
        {
          dataKey: "currAss",
          stack: "assets",
          label: "Current Assets",
          valueFormatter: (v: number | null) => (typeof v === "number" ? `$${v.toLocaleString()}K` : "-"),
        },
        {
          dataKey: "nCurrAss",
          stack: "assets",
          label: "non-Current Assets",
          valueFormatter: (v: number | null) => (typeof v === "number" ? `$${v.toLocaleString()}K` : "-"),
        },
        {
          dataKey: "curLia",
          stack: "liability",
          label: "Current Liabilities",
          valueFormatter: (v: number | null) => (typeof v === "number" ? `$${v.toLocaleString()}K` : "-"),
        },
        {
          dataKey: "nCurLia",
          stack: "liability",
          label: "non-Current Liabilities",
          valueFormatter: (v: number | null) => (typeof v === "number" ? `$${v.toLocaleString()}K` : "-"),
        },
        {
          dataKey: "capStock",
          stack: "equity",
          label: "Capital Stock",
          valueFormatter: (v: number | null) => (typeof v === "number" ? `$${v.toLocaleString()}K` : "-"),
        },
        {
          dataKey: "retEarn",
          stack: "equity",
          label: "Retained Earning",
          valueFormatter: (v: number | null) => (typeof v === "number" ? `$${v.toLocaleString()}K` : "-"),
        },
        {
          dataKey: "treas",
          stack: "equity",
          label: "Treasury",
          valueFormatter: (v: number | null) => (typeof v === "number" ? `$${v.toLocaleString()}K` : "-"),
        },
      ]}
      xAxis={[{ categoryGapRatio: 0.5, barGapRatio: 0.2, disableLine: true, disableTicks: true, dataKey: "year" }]}
      yAxis={[
        { disableLine: true, disableTicks: true, valueFormatter: (value: number) => `${Math.round(value / 1000000)}M` },
      ]}
      height={300}
      hideLegend
      slots={{ tooltip: CustomChartTooltip, bar: withChartElementStyle(BarElement, { rx: 5, ry: 5 }) }}
      grid={{ horizontal: true }}
      {...chartPalette}
    />
  );
}

