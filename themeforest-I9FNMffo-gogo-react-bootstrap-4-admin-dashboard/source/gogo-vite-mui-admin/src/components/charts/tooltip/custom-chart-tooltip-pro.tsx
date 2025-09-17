import { ChartsTooltipContainer, ChartsTooltipPaper, ChartsTooltipProps } from "@mui/x-charts-pro";

import CustomChartTooltipContent from "@/components/charts/tooltip/custom-chart-tooltip-content";
import useChartTooltipDataPro from "@/hooks/use-chart-tooltip-data-pro";

export default function CustomChartTooltipPro(props: Readonly<ChartsTooltipProps>) {
  const { trigger, hideTitle } = props;
  const tooltipData = useChartTooltipDataPro(trigger);

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
