import dayjs from "dayjs";

import { GridFilterInputValueProps } from "@mui/x-data-grid-pro";
import { DateTimePicker } from "@mui/x-date-pickers";

import NiCalendar from "@/template_full/icons/nexture/ni-calendar";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftSmall from "@/template_full/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import { cn } from "@/template_full/lib/utils";

export default function DataGridDateTimeFilter(props: GridFilterInputValueProps) {
  const { item, applyValue, apiRef } = props;

  const handleChange = (newValue: unknown) => {
    applyValue({ ...item, value: newValue });
  };

  return (
    <DateTimePicker
      defaultValue={item.value ? dayjs(item.value) : null}
      onChange={handleChange}
      label={apiRef.current.getLocaleText("filterPanelInputLabel")}
      className="outlined edit-date mb-0"
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
  );
}

