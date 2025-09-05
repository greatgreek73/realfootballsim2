import dayjs from "dayjs";
import { SyntheticEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import {
  Autocomplete,
  Avatar,
  Box,
  Card,
  CardContent,
  FormControl,
  FormLabel,
  InputAdornment,
  TextField,
  Typography,
} from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";

import NiCalendar from "@/template_full/icons/nexture/ni-calendar";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftSmall from "@/template_full/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import NiCross from "@/template_full/icons/nexture/ni-cross";
import { cn } from "@/template_full/lib/utils";

interface UserType {
  id: string;
  name: string;
  image: string;
}

interface IssueData {
  assignee: UserType;
  assigneeList: UserType[];
}

export default function LPInputs() {
  const [issue, setIssue] = useState<IssueData>({
    assignee: {
      id: "2222",
      name: "Sofia Bennett",
      image: "/images/avatars/avatar-3.jpg",
    },
    assigneeList: [
      {
        id: "2220",
        name: "Laura Ellis",
        image: "/images/avatars/avatar-1.jpg",
      },
      {
        id: "2221",
        name: "Daniel Fontaine",
        image: "/images/avatars/avatar-2.jpg",
      },
      {
        id: "2222",
        name: "Sofia Bennett",
        image: "/images/avatars/avatar-3.jpg",
      },
      {
        id: "2223",
        name: "Olivia Castillo",
        image: "/images/avatars/avatar-4.jpg",
      },
      {
        id: "2224",
        name: "Lucas Wright",
        image: "/images/avatars/avatar-5.jpg",
      },
      {
        id: "2225",
        name: "Adrian Patel",
        image: "/images/avatars/avatar-6.jpg",
      },
      {
        id: "2226",
        name: "Henry Lawson",
        image: "/images/avatars/avatar-7.jpg",
      },
      {
        id: "2227",
        name: "Emma Sullivan",
        image: "/images/avatars/avatar-8.jpg",
      },
    ],
  });

  const handleAssigneeChange = (_: SyntheticEvent, value: any) => {
    if (value) {
      const selectedUser = issue.assigneeList.find((user: any) => {
        return user.id === value.id;
      });
      setIssue({ ...issue, assignee: selectedUser as UserType });
    } else {
      setIssue({
        ...issue,
        assignee: {
          id: "",
          name: "",
          image: "",
        },
      });
    }
  };

  const [dateOpen, setDateOpen] = useState(false);
  const { t } = useTranslation();

  return (
    <Card className="w-[280px]">
      <CardContent>
        <FormControl fullWidth>
          <FormLabel component="label"> {t("landing-assignee")}</FormLabel>
          <Autocomplete
            size="small"
            options={issue.assigneeList}
            popupIcon={<NiChevronDownSmall />}
            clearIcon={<NiCross />}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            autoHighlight
            getOptionLabel={(option) => option.name}
            getOptionKey={(option) => option.id}
            value={issue.assignee}
            renderOption={(props, option) => {
              const { key, ...optionProps } = props;
              return (
                <Box component="li" key={key} {...optionProps}>
                  <Box className="flex flex-row items-center gap-1.5">
                    <Avatar alt={option.name} src={option.image} className="rounded-2xs h-5! w-5!" />
                    <Typography>{option.name}</Typography>
                  </Box>
                </Box>
              );
            }}
            slotProps={{
              popper: { className: "outlined" },
              chip: {
                variant: "filled",
                size: "small",
              },
            }}
            renderInput={(params) => {
              return (
                <TextField
                  {...params}
                  variant="standard"
                  className="outlined"
                  placeholder={t("landing-assignee")}
                  slotProps={{
                    htmlInput: {
                      ...params.inputProps,
                      autoComplete: "new-password",
                    },
                    input: {
                      ...params.InputProps,
                      startAdornment: (
                        <>
                          <InputAdornment position="start">
                            {issue.assignee?.image && (
                              <Avatar
                                alt={issue.assignee.name}
                                src={issue.assignee.image}
                                className="rounded-2xs mr-1.5 h-5! w-5!"
                              />
                            )}
                          </InputAdornment>
                          {params.InputProps.startAdornment}
                        </>
                      ),
                    },
                  }}
                />
              );
            }}
            onChange={handleAssigneeChange}
          />
        </FormControl>

        <FormControl fullWidth variant="standard" className="outlined mb-0">
          <FormLabel component="label">{t("landing-date")}</FormLabel>
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DatePicker
              className="mb-0"
              open={dateOpen}
              onOpen={() => setDateOpen(true)}
              onClose={() => setDateOpen(false)}
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
                  variant: "standard",
                  onClick: () => setDateOpen(true),
                },
                desktopPaper: { className: "outlined" },
              }}
              defaultValue={dayjs("2025-04-17")}
            />
          </LocalizationProvider>
        </FormControl>
      </CardContent>
    </Card>
  );
}

