import { useTranslation } from "react-i18next";

import Timeline from "@mui/lab/Timeline";
import TimelineConnector from "@mui/lab/TimelineConnector";
import TimelineContent from "@mui/lab/TimelineContent";
import TimelineDot from "@mui/lab/TimelineDot";
import TimelineItem from "@mui/lab/TimelineItem";
import TimelineSeparator from "@mui/lab/TimelineSeparator";
import { Card, CardContent, Typography } from "@mui/material";

import NiCar from "@/icons/nexture/ni-car";
import NiChef from "@/icons/nexture/ni-chef";
import NiEyeInactive from "@/icons/nexture/ni-eye-inactive";

export default function LPTimeline() {
  const { t } = useTranslation();

  return (
    <Card className="w-[200px]">
      <CardContent>
        <Timeline>
          <TimelineItem>
            <TimelineSeparator>
              <TimelineConnector />
              <TimelineDot className="bg-primary-light/10 text-primary rounded-lg p-2">
                <NiChef />
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent className="py-4">
              <Typography variant="h6" component="span">
                {t("landing-eat")}
              </Typography>
              <Typography variant="body2" className="text-text-secondary">
                08:00
              </Typography>
            </TimelineContent>
          </TimelineItem>

          <TimelineItem>
            <TimelineSeparator>
              <TimelineConnector />
              <TimelineDot className="bg-secondary-light/10 text-secondary rounded-lg p-2">
                <NiCar />
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent className="py-4">
              <Typography variant="h6" component="span">
                {t("landing-drive")}
              </Typography>
              <Typography variant="body2" className="text-text-secondary">
                09:00
              </Typography>
            </TimelineContent>
          </TimelineItem>
          <TimelineItem>
            <TimelineSeparator>
              <TimelineConnector />
              <TimelineDot className="bg-accent-1-light/10 text-accent-1 rounded-lg p-2">
                <NiEyeInactive />
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent className="py-4">
              <Typography variant="h6" component="span">
                {t("landing-sleep")}
              </Typography>
              <Typography variant="body2" className="text-text-secondary">
                00:00
              </Typography>
            </TimelineContent>
          </TimelineItem>
        </Timeline>
      </CardContent>
    </Card>
  );
}
