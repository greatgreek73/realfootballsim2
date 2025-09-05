import { ChartsTooltipProps, useAxesTooltip, useItemTooltip } from "@mui/x-charts";

import { tooltipHooksToDataset } from "@/template_full/lib/chart-helper";

export default function useChartTooltipData(trigger: ChartsTooltipProps["trigger"] = "axis") {
  const axesTooltip = useAxesTooltip();
  const itemTooltip = useItemTooltip();

  return tooltipHooksToDataset({ axesTooltip, itemTooltip, trigger });
}

