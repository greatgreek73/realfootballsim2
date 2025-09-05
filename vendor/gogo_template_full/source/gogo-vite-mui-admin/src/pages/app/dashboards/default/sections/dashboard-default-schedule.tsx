import { SyntheticEvent, useState } from "react";

import { Box, Card, CardContent, Tab, Tabs, Typography } from "@mui/material";

import NiBag from "@/icons/nexture/ni-bag";
import NiChef from "@/icons/nexture/ni-chef";
import NiChevronLeftSmall from "@/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";
import NiPresentation from "@/icons/nexture/ni-presentation";

export default function DashboardDefaultSchedule() {
  const [tabValue, setTabValue] = useState(0);

  const handleChange = (_event: SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Card className="h-full">
      <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
        Schedule
      </Typography>
      <CardContent className="px-0! pt-0!">
        <Tabs
          className="flex grow"
          classes={{ flexContainer: "gap-2 flex grow" }}
          value={tabValue}
          onChange={handleChange}
          variant="scrollable"
          allowScrollButtonsMobile
          scrollButtons={true}
          slots={{
            EndScrollButtonIcon: (props) => {
              return <NiChevronRightSmall size="medium" {...props} />;
            },
            StartScrollButtonIcon: (props) => {
              return <NiChevronLeftSmall size="medium" {...props} />;
            },
          }}
        >
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">Mo</Typography>
                <Typography className="text-primary">18</Typography>
              </Box>
            }
          />
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">Tu</Typography>
                <Typography className="text-primary">19</Typography>
              </Box>
            }
          />
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">We</Typography>
                <Typography className="text-primary">20</Typography>
              </Box>
            }
          />
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">Th</Typography>
                <Typography className="text-primary">21</Typography>
              </Box>
            }
          />
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">Fr</Typography>
                <Typography className="text-primary">22</Typography>
              </Box>
            }
          />
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">Sa</Typography>
                <Typography className="text-primary">23</Typography>
              </Box>
            }
          />
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">Su</Typography>
                <Typography className="text-primary">24</Typography>
              </Box>
            }
          />
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">Mo</Typography>
                <Typography className="text-primary">25</Typography>
              </Box>
            }
          />
          <Tab
            className="w-10 [&:not(.Mui-selected)]:border-transparent"
            label={
              <Box className="flex flex-col">
                <Typography className="text-text-secondary">Tu</Typography>
                <Typography className="text-primary">26</Typography>
              </Box>
            }
          />
        </Tabs>
        <Box className="px-4">
          <Typography className="mb-5">18 May 2025 Monday</Typography>
          <Box className="flex flex-col gap-4">
            <Box className="flex flex-row gap-2.5">
              <NiBag className="text-primary flex-none"></NiBag>
              <Box>
                <Typography variant="subtitle2">Client Meeting</Typography>
                <Typography variant="body2" className="text-text-secondary">
                  Short introduction with the new client
                </Typography>
                <Typography variant="body2" className="text-text-secondary">
                  10:30 AM
                </Typography>
              </Box>
            </Box>

            <Box className="flex flex-row gap-2.5">
              <NiPresentation className="text-secondary flex-none"></NiPresentation>
              <Box>
                <Typography variant="subtitle2">Sprint Planning</Typography>
                <Typography variant="body2" className="text-text-secondary">
                  Weekly sprint planning
                </Typography>
                <Typography variant="body2" className="text-text-secondary">
                  02:30 PM
                </Typography>
              </Box>
            </Box>

            <Box className="flex flex-row gap-2.5">
              <NiChef className="text-accent-1 flex-none"></NiChef>
              <Box>
                <Typography variant="subtitle2">Team Lunch</Typography>
                <Typography variant="body2" className="text-text-secondary">
                  Frontend team meetup and lunch
                </Typography>
                <Typography variant="body2" className="text-text-secondary">
                  12:30 PM
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
