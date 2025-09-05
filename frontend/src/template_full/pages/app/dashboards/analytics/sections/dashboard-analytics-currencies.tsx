import dayjs from "dayjs";

import { Box, Card, CardContent, Grid, Typography, useTheme } from "@mui/material";
import { SparkLineChart } from "@mui/x-charts";

import useHighlightedSparkline from "@/template_full/hooks/use-highlighted-sparkline";
import NiTriangleDown from "@/template_full/icons/nexture/ni-triangle-down";
import NiTriangleUp from "@/template_full/icons/nexture/ni-triangle-up";

const btcUsdData = [8000, 8300, 9000, 9000, 9500, 9800, 9800, 9400, 9548.31];
const ethUsdData = [110, 120, 125, 125, 140, 150, 150, 130, 128.42];
const xrpUsdData = [80, 90, 100, 100, 120, 130, 130, 100, 104.25];

export default function DashboardAnalyticsCurrencies() {
  const { palette } = useTheme();

  const btcUsdSparkline = useHighlightedSparkline({
    data: btcUsdData,
    plotType: "line",
    color: palette.primary.main,
  });
  const ethUsdSparkline = useHighlightedSparkline({
    data: ethUsdData,
    plotType: "line",
    color: palette.primary.main,
  });
  const xrpUsdSparkline = useHighlightedSparkline({
    data: xrpUsdData,
    plotType: "line",
    color: palette.primary.main,
  });

  return (
    <Grid container size={12} spacing={2.5}>
      <Grid size={{ xs: 12 }}>
        <Card className="h-24">
          <CardContent className="flex items-center gap-5">
            <Box className="flex-shrink-0">
              <Typography variant="body1" className="w-54">
                BTC / USD
                <Typography variant="body1" component="span" className="text-text-secondary-light">
                  {" - "}
                  {dayjs()
                    .subtract(btcUsdSparkline.props.data.length - btcUsdSparkline.item.index - 1, "day")
                    .format("MMMM D dddd")}
                </Typography>
              </Typography>
              <Box className="flex items-center gap-1">
                <Typography variant="h5" className="text-text-primary">
                  {btcUsdSparkline.item.value.toLocaleString()}
                </Typography>
                <ChangeStatus change={btcUsdSparkline.item.change} />
              </Box>
            </Box>
            <Box className="-my-1 grow">
              <SparkLineChart {...btcUsdSparkline.props} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12 }}>
        <Card className="h-24">
          <CardContent className="flex items-center gap-5">
            <Box className="flex-shrink-0">
              <Typography variant="body1" className="w-54">
                ETH / USD
                <Typography variant="body1" component="span" className="text-text-secondary-light">
                  {" - "}
                  {dayjs()
                    .subtract(ethUsdSparkline.props.data.length - ethUsdSparkline.item.index - 1, "day")
                    .format("MMMM D dddd")}
                </Typography>
              </Typography>
              <Box className="flex items-center gap-1">
                <Typography variant="h5" className="text-text-primary">
                  {ethUsdSparkline.item.value.toLocaleString()}
                </Typography>
                <ChangeStatus change={ethUsdSparkline.item.change} />
              </Box>
            </Box>
            <Box className="-my-1 grow">
              <SparkLineChart {...ethUsdSparkline.props} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12 }}>
        <Card className="h-24">
          <CardContent className="flex items-center gap-5">
            <Box className="flex-shrink-0">
              <Typography variant="body1" className="w-54">
                XRP / USD
                <Typography variant="body1" component="span" className="text-text-secondary-light">
                  {" - "}
                  {dayjs()
                    .subtract(xrpUsdSparkline.props.data.length - xrpUsdSparkline.item.index - 1, "day")
                    .format("MMMM D dddd")}
                </Typography>
              </Typography>
              <Box className="flex items-center gap-1">
                <Typography variant="h5" className="text-text-primary">
                  {xrpUsdSparkline.item.value.toLocaleString()}
                </Typography>
                <ChangeStatus change={xrpUsdSparkline.item.change} />
              </Box>
            </Box>
            <Box className="-my-1 grow">
              <SparkLineChart {...xrpUsdSparkline.props} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

const ChangeStatus = ({ change }: { change: number | string }) => {
  return (
    <Box className="flex">
      {Number(change) < 0 ? (
        <NiTriangleDown size="tiny" className="text-error" />
      ) : (
        <NiTriangleUp size="tiny" className="text-success" />
      )}
      <Typography variant="body2" className={Number(change) < 0 ? "text-error" : "text-success"}>
        {Math.abs(Number(change))}%
      </Typography>
    </Box>
  );
};

