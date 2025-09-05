import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import relativeTime from "dayjs/plugin/relativeTime";

import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Link,
  Rating,
  Select,
  SelectProps,
  Toolbar,
  Typography,
} from "@mui/material";
import { GridActionsCellItem, GridRenderCellParams } from "@mui/x-data-grid";
import { DataGridPro, GridColDef } from "@mui/x-data-grid-pro";

import NiArrowDown from "@/template_full/icons/nexture/ni-arrow-down";
import NiArrowInDown from "@/template_full/icons/nexture/ni-arrow-in-down";
import NiArrowUp from "@/template_full/icons/nexture/ni-arrow-up";
import NiBinEmpty from "@/template_full/icons/nexture/ni-bin-empty";
import NiCheckSquare from "@/template_full/icons/nexture/ni-check-square";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftRightSmall from "@/template_full/icons/nexture/ni-chevron-left-right-small";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import NiCols from "@/template_full/icons/nexture/ni-cols";
import NiCross from "@/template_full/icons/nexture/ni-cross";
import NiCrossSquare from "@/template_full/icons/nexture/ni-cross-square";
import NiDuplicate from "@/template_full/icons/nexture/ni-duplicate";
import NiEllipsisVertical from "@/template_full/icons/nexture/ni-ellipsis-vertical";
import NiExclamationSquare from "@/template_full/icons/nexture/ni-exclamation-square";
import NiExpand from "@/template_full/icons/nexture/ni-expand";
import NiEyeInactive from "@/template_full/icons/nexture/ni-eye-inactive";
import NiFilter from "@/template_full/icons/nexture/ni-filter";
import NiFilterPlus from "@/template_full/icons/nexture/ni-filter-plus";
import NiPlus from "@/template_full/icons/nexture/ni-plus";
import NiPlusSquare from "@/template_full/icons/nexture/ni-plus-square";
import NiPushPinLeft from "@/template_full/icons/nexture/ni-push-pin-left";
import NiPushPinRight from "@/template_full/icons/nexture/ni-push-pin-right";
import NiSearch from "@/template_full/icons/nexture/ni-search";
import NiStar from "@/template_full/icons/nexture/ni-star";

dayjs.extend(duration);
dayjs.extend(relativeTime);

export default function DashboardVisualRecentReviews() {
  function GridCustomToolbar() {
    return (
      <Toolbar className="flex flex-row items-start">
        <Typography variant="h5" component="h5" className="card-title flex-1">
          Recent Reviews
        </Typography>
        <Button size="tiny" color="grey" variant="text" startIcon={<NiChevronRightSmall size={"tiny"} />}>
          View All
        </Button>
      </Toolbar>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box className="h-[360px]">
          <DataGridPro
            rows={rows}
            columns={columns}
            hideFooter
            disableColumnFilter
            disableColumnSelector
            disableDensitySelector
            columnHeaderHeight={40}
            disableRowSelectionOnClick
            className="border-none"
            showToolbar
            slots={{
              toolbar: GridCustomToolbar,
              columnSortedDescendingIcon: () => {
                return <NiArrowDown size={"small"}></NiArrowDown>;
              },
              columnSortedAscendingIcon: () => {
                return <NiArrowUp size={"small"}></NiArrowUp>;
              },
              columnFilteredIcon: () => {
                return <NiFilterPlus size={"small"}></NiFilterPlus>;
              },
              columnReorderIcon: () => {
                return <NiChevronLeftRightSmall size={"small"}></NiChevronLeftRightSmall>;
              },
              columnMenuIcon: () => {
                return <NiEllipsisVertical size={"small"}></NiEllipsisVertical>;
              },
              columnMenuSortAscendingIcon: NiArrowUp,
              columnMenuSortDescendingIcon: NiArrowDown,
              columnMenuFilterIcon: NiFilter,
              columnMenuHideIcon: NiEyeInactive,
              columnMenuClearIcon: NiCross,
              columnMenuManageColumnsIcon: NiCols,
              columnMenuPinLeftIcon: NiPushPinLeft,
              columnMenuPinRightIcon: NiPushPinRight,
              filterPanelDeleteIcon: NiCross,
              filterPanelAddIcon: NiPlus,
              filterPanelRemoveAllIcon: NiBinEmpty,
              columnSelectorIcon: NiCols,
              exportIcon: NiArrowInDown,
              openFilterButtonIcon: NiFilter,
              baseSelect: (props) => {
                const propsCasted = props as SelectProps;
                return (
                  <FormControl size="small" variant="outlined">
                    <InputLabel>{props.label}</InputLabel>
                    <Select {...propsCasted} IconComponent={NiChevronDownSmall} MenuProps={{ className: "outlined" }} />
                  </FormControl>
                );
              },
              quickFilterIcon: () => {
                return <NiSearch size={"medium"} />;
              },
              quickFilterClearIcon: () => {
                return <NiCross size={"medium"} />;
              },
              baseButton: (props) => {
                return <Button {...props} variant="pastel" color="grey"></Button>;
              },
              moreActionsIcon: () => {
                return <NiEllipsisVertical size={"medium"} />;
              },
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
}

const columns: GridColDef<(typeof rows)[number]>[] = [
  {
    field: "image",
    headerName: "Image",
    width: 60,
    editable: false,
    filterable: false,
    renderCell: (params: GridRenderCellParams<any, string>) => (
      <Box className="flex h-full items-center">
        <img src={params.value as string} alt="grid image" className="h-9 w-9 rounded-sm object-cover" />
      </Box>
    ),
  },
  { field: "id", headerName: "ID", width: 60 },
  {
    field: "message",
    headerName: "Message",
    width: 220,
    renderCell: (params: GridRenderCellParams<any, string>) => (
      <Link href="#" variant="body1" underline="hover" className="text-text-primary">
        {params.value}
      </Link>
    ),
  },
  {
    field: "rating",
    headerName: "Rating",
    align: "left",
    headerAlign: "left",
    type: "number",
    width: 120,
    renderCell: (params: GridRenderCellParams<any, number>) => (
      <Rating
        readOnly
        size="small"
        precision={0.5}
        defaultValue={params.value}
        max={5}
        icon={<NiStar variant="contained" size="small" />}
        emptyIcon={<NiStar size="small" className="outlined" />}
      />
    ),
  },
  {
    field: "status",
    headerName: "Status",
    align: "left",
    headerAlign: "left",
    minWidth: 100,
    flex: 1,
    type: "singleSelect",
    valueOptions: ["Active", "Done", "Pending"],
    renderCell: (params: GridRenderCellParams<any, string>) => {
      const value = params.value;
      if (value === "Active") {
        return (
          <Button
            className="icon-only pointer-events-none self-center"
            size="tiny"
            color="success"
            variant="pastel"
            startIcon={<NiPlusSquare size={"tiny"} />}
          />
        );
      } else if (value === "Done") {
        return (
          <Button
            className="icon-only pointer-events-none self-center"
            size="tiny"
            color="info"
            variant="pastel"
            startIcon={<NiCheckSquare size={"tiny"} />}
          />
        );
      } else {
        return (
          <Button
            className="icon-only pointer-events-none self-center"
            size="tiny"
            color="warning"
            variant="pastel"
            startIcon={<NiExclamationSquare size={"tiny"} />}
          />
        );
      }
    },
  },
  {
    field: "actions",
    headerName: "Actions",
    type: "actions",
    minWidth: 80,
    flex: 1,
    align: "right",
    headerAlign: "right",
    getActions: () => [
      <GridActionsCellItem key={1} icon={<NiExpand size="medium" />} label="View" showInMenu />,
      <GridActionsCellItem key={2} icon={<NiDuplicate size="medium" />} label="Duplicate" showInMenu />,
      <GridActionsCellItem key={0} icon={<NiCrossSquare size="medium" />} label="Delete" showInMenu />,
    ],
  },
];

const rows = [
  {
    id: 472,
    image: "/images/avatars/avatar-1.jpg",
    message: "Billing page returns error",
    rating: 5,
    status: "Active",
  },
  {
    id: 473,
    image: "/images/avatars/avatar-2.jpg",
    message: "Book availability/restocking",
    rating: 5,
    status: "Active",
  },
  {
    id: 474,
    image: "/images/avatars/avatar-3.jpg",
    message: "Placing bulk book orders for our school",
    rating: 4.5,
    status: "Active",
  },
  {
    id: 475,
    image: "/images/avatars/avatar-4.jpg",
    message: "Need help with membership benefits",
    rating: 4,
    status: "Done",
  },
  {
    id: 476,
    image: "/images/avatars/avatar-5.jpg",
    message: "Pre-ordering special edition releases",
    rating: 4,
    status: "Done",
  },
  {
    id: 477,
    image: "/images/avatars/avatar-6.jpg",
    message: "Issue with a recent order payment",
    rating: 5,
    status: "Pending",
  },
  {
    id: 478,
    image: "/images/avatars/avatar-7.jpg",
    message: "I am receiving a 404 error",
    rating: 5,
    status: "Pending",
  },
  {
    id: 479,
    image: "/images/avatars/avatar-8.jpg",
    message: "The writer name spelling error",
    rating: 5,
    status: "Pending",
  },
];

