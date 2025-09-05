import { Card, CardContent, Typography, useTheme } from "@mui/material";
import { RadarChart } from "@mui/x-charts";

import CustomChartMark from "@/template_full/components/charts/mark/custom-chart-mark";
import CustomChartTooltip from "@/template_full/components/charts/tooltip/custom-chart-tooltip";

export default function DashboardAnalyticsOrdersStocks() {
  const { palette } = useTheme();

  return (
    <Card className="h-96">
      <CardContent>
        <Typography variant="h5" component="h5" className="card-title">
          Orders vs Stocks
        </Typography>

        <RadarChart
          series={[
            {
              label: "Order",
              data: [200, 300, 600],
              color: palette.primary.main,
              fillArea: true,
              labelMarkType: CustomChartMark,
            },
            {
              label: "Stock",
              data: [700, 600, 200],
              color: palette.secondary.main,
              fillArea: true,
              labelMarkType: CustomChartMark,
            },
          ]}
          className="radar-chart order-first min-w-50"
          shape="sharp"
          radar={{ labelGap: 6, max: 1000, metrics: ["Books", "Games", "Toys"] }}
          divisions={3}
          height={270}
          margin={{ left: 30, right: 34 }}
          slots={{ tooltip: CustomChartTooltip }}
          stripeColor={null}
        />
      </CardContent>
    </Card>
  );
}

