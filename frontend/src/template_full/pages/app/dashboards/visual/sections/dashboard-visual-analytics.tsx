import { Button, Card, CardContent, Typography } from "@mui/material";

import IllustrationAnalytics from "@/template_full/icons/illustrations/illustration-analytics";
import NiChartPolar from "@/template_full/icons/nexture/ni-chart-polar";

export default function DashboardVisualAnalytics() {
  return (
    <Card className="h-full">
      <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
        Analytics
      </Typography>
      <CardContent className="flex flex-col items-center gap-5 pt-0!">
        <IllustrationAnalytics className="text-primary max-h-56 w-full object-contain" />

        <Typography component="p" className="text-center">
          Configure analytics to get extended results!
        </Typography>
        <Button size="medium" color="primary" variant="contained" startIcon={<NiChartPolar size={"medium"} />}>
          Get Analytics
        </Button>
      </CardContent>
    </Card>
  );
}

