import { ChartsTooltipContainer, ChartsTooltipPaper, ChartsTooltipProps } from "@mui/x-charts";

import CustomChartTooltipContent from "@/components/charts/tooltip/custom-chart-tooltip-content";
import useChartTooltipData from "@/hooks/use-chart-tooltip-data";

export default function CustomChartTooltip(props: Readonly<ChartsTooltipProps>) {
  const { trigger, hideTitle } = props;
  const tooltipData = useChartTooltipData(trigger);

  return (
    <CustomChartTooltipContent
      hideTitle={hideTitle}
      data={tooltipData}
      ContentContainer={ChartsTooltipContainer}
      ContentPaper={ChartsTooltipPaper}
      {...props}
    />
  );
}
