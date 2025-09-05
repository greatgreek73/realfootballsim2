import dayjs from "dayjs";

import { Box, FormControl } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DateRangePicker, MultiInputDateRangeField, SingleInputDateRangeField } from "@mui/x-date-pickers-pro";

import NiCalendar from "@/template_full/icons/nexture/ni-calendar";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftSmall from "@/template_full/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import { cn } from "@/template_full/lib/utils";

export default function DateRangeOutlined() {
  return (
    <Box className="flex flex-col">
      <FormControl fullWidth variant="outlined" size="small">
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DateRangePicker
            className="mb-0"
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
            }}
            slotProps={{
              textField: {
                size: "small",
                variant: "outlined",
                label: "Date Range",
              },
              desktopPaper: { className: "outlined" },
            }}
          />
        </LocalizationProvider>
      </FormControl>
      <FormControl fullWidth variant="outlined" className="mb-0">
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <MultiInputDateRangeField
            className="mb-0"
            slotProps={{
              textField: ({ position }) => ({
                label: position === "start" ? "Field Start" : "Field End",
                size: "small",
                variant: "outlined",
              }),
            }}
          />
        </LocalizationProvider>
      </FormControl>
      <FormControl fullWidth variant="outlined">
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DateRangePicker
            className="mb-0"
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
            }}
            slotProps={{
              textField: {
                size: "small",
                variant: "outlined",
                label: "Readonly",
              },
              desktopPaper: { className: "outlined" },
            }}
            readOnly
            defaultValue={[dayjs("2025-04-17"), dayjs("2025-04-21")]}
          />
        </LocalizationProvider>
      </FormControl>

      <FormControl fullWidth variant="outlined">
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DateRangePicker
            disabled
            className="mb-0"
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
            }}
            slotProps={{
              textField: {
                size: "small",
                variant: "outlined",
                label: "Disabled",
              },
              desktopPaper: { className: "outlined" },
            }}
            defaultValue={[dayjs("2025-04-17"), dayjs("2025-04-21")]}
          />
        </LocalizationProvider>
      </FormControl>

      <FormControl fullWidth variant="outlined" size="medium">
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DateRangePicker
            className="mb-0"
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
            }}
            slotProps={{
              textField: {
                size: "medium",
                variant: "outlined",
                label: "Medium",
              },
              desktopPaper: { className: "outlined" },
            }}
          />
        </LocalizationProvider>
      </FormControl>

      <FormControl fullWidth variant="outlined">
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DateRangePicker
            className="mb-0"
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
              field: SingleInputDateRangeField,
            }}
            slotProps={{
              textField: {
                size: "small",
                variant: "outlined",
                label: "Single Input",
              },
              desktopPaper: { className: "outlined" },
            }}
          />
        </LocalizationProvider>
      </FormControl>

      <FormControl fullWidth variant="outlined" className="mb-0">
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <SingleInputDateRangeField
            className="mb-0"
            slotProps={{
              textField: {
                label: "Field Single Input",
                size: "small",
                variant: "outlined",
              },
            }}
          />
        </LocalizationProvider>
      </FormControl>
    </Box>
  );
}

