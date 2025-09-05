import { FormControl, FormLabel } from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers-pro";
import { AdapterDayjs } from "@mui/x-date-pickers-pro/AdapterDayjs";

import NiCalendar from "@/template_full/icons/nexture/ni-calendar";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftSmall from "@/template_full/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import { cn } from "@/template_full/lib/utils";

export default function DateTimePickerProVersion() {
  return (
    <FormControl className="outlined mb-0" fullWidth>
      <FormLabel component="label">Date Picker</FormLabel>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <DatePicker
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
            textField: { size: "small", variant: "standard" },
            desktopPaper: { className: "outlined" },
          }}
        />
      </LocalizationProvider>
    </FormControl>
  );
}

