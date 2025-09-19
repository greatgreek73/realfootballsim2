import DashboardVisualAnalytics from "./sections/dashboard-visual-analytics";
import DashboardVisualCategories from "./sections/dashboard-visual-categories";
import DashboardVisualHelp from "./sections/dashboard-visual-help";
import DashboardVisualPost from "./sections/dashboard-visual-post";
import DashboardVisualRecentReviews from "./sections/dashboard-visual-reviews";
import DashboardVisualStats from "./sections/dashboard-visual-stats";
import DashboardVisualStocks from "./sections/dashboard-visual-stocks";
import DashboardVisualTasks from "./sections/dashboard-visual-tasks";
import DashboardVisualRecentTickets from "./sections/dashboard-visual-tickets";
import dayjs, { Dayjs } from "dayjs";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Breadcrumbs, Button, FormControl, Tooltip, Typography } from "@mui/material";
import { Grid } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers-pro";
import { AdapterDayjs } from "@mui/x-date-pickers-pro/AdapterDayjs";
import { DateRange, DateRangePicker } from "@mui/x-date-pickers-pro";

import NiCalendar from "@/icons/nexture/ni-calendar";
import NiCellsPlus from "@/icons/nexture/ni-cells-plus";
import NiChevronDownSmall from "@/icons/nexture/ni-chevron-down-small";
import NiChevronLeftSmall from "@/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";
import NiCross from "@/icons/nexture/ni-cross";
import NiKnobs from "@/icons/nexture/ni-knobs";
import { cn } from "@/lib/utils";

export default function Page() {
  const [dateRange, setDateRange] = useState<DateRange<Dayjs>>([dayjs("2022-04-17"), dayjs("2022-04-21")]);

  return (
    <Grid container spacing={5}>
      <Grid container spacing={2.5} className="w-full" size={12}>
        <Grid size={{ xs: 12, md: "grow" }}>
          <Typography variant="h1" component="h1" className="mb-0">
            Welcome Laura!
          </Typography>
          <Breadcrumbs>
            <Link color="inherit" to="/dashboards/default">
              Home
            </Link>
            <Link color="inherit" to="/dashboards">
              Dashboards
            </Link>
            <Typography variant="body2">Visual</Typography>
          </Breadcrumbs>
        </Grid>

        <Grid size={{ xs: 12, md: "auto" }} className="flex flex-row items-start gap-2">
          <FormControl variant="standard" className="surface-standard mb-0 w-full md:w-auto">
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DateRangePicker
                slots={{
                  openPickerIcon: (props) => {
                    return <NiCalendar {...props} className={cn(props.className, "text-text-secondary")} />;
                  },
                  switchViewIcon: (props) => {
                    return <NiChevronDownSmall {...props} className={cn(props.className, "text-text-secondary")} />;
                  },
                  leftArrowIcon: (props) => {
                    return <NiChevronLeftSmall {...props} className={cn(props.className, "text-text-secondary")} />;
                  },
                  rightArrowIcon: (props) => {
                    return <NiChevronRightSmall {...props} className={cn(props.className, "text-text-secondary")} />;
                  },
                  clearIcon: (props) => {
                    return <NiCross {...props} className={cn(props.className, "text-text-secondary")} />;
                  },
                }}
                slotProps={{
                  textField: { size: "small", variant: "standard" },
                  desktopPaper: { className: "outlined" },
                }}
                value={dateRange}
                onChange={(newValue) => setDateRange(newValue)}
              />
            </LocalizationProvider>
          </FormControl>

          <Tooltip title="Configuration">
            <Button
              className="icon-only surface-standard flex-none"
              size="medium"
              color="grey"
              variant="surface"
              startIcon={<NiKnobs size={"medium"} />}
            />
          </Tooltip>
          <Tooltip title="Add Widget">
            <Button
              className="icon-only surface-standard flex-none"
              size="medium"
              color="grey"
              variant="surface"
              startIcon={<NiCellsPlus size={"medium"} />}
            />
          </Tooltip>
        </Grid>
      </Grid>

      <Grid container size={12}>
        <Grid size={{ lg: 6, xs: 12 }} container spacing={2.5}>
          <DashboardVisualStats />
        </Grid>

        <Grid size={{ lg: 6, xs: 12 }}>
          <DashboardVisualPost />
        </Grid>
      </Grid>

      <Grid container size={12}>
        <Grid size={{ lg: 6, xs: 12 }}>
          <DashboardVisualTasks />
        </Grid>

        <Grid size={{ lg: 6, xs: 12 }}>
          <DashboardVisualCategories />
        </Grid>
      </Grid>

      <Grid container size={12}>
        <Grid size={{ "2xl": 6, xs: 12 }}>
          <DashboardVisualRecentTickets />
        </Grid>

        <Grid size={{ "2xl": 3, md: 6, xs: 12 }}>
          <DashboardVisualAnalytics />
        </Grid>

        <Grid size={{ "2xl": 3, md: 6, xs: 12 }}>
          <DashboardVisualStocks />
        </Grid>
      </Grid>

      <Grid container size={12}>
        <Grid size={{ lg: 6, xs: 12 }}>
          <DashboardVisualHelp />
        </Grid>

        <Grid size={{ lg: 6, xs: 12 }}>
          <DashboardVisualRecentReviews />
        </Grid>
      </Grid>
    </Grid>
  );
}
