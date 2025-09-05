import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import relativeTime from "dayjs/plugin/relativeTime";

import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  InputAdornment,
  InputLabel,
  Link,
  Select,
  SelectProps,
  TextField,
  Toolbar,
  Typography,
} from "@mui/material";
import { GridRenderCellParams, QuickFilter, QuickFilterClear, QuickFilterControl } from "@mui/x-data-grid";
import { DataGridPro, GridColDef } from "@mui/x-data-grid-pro";

import NiArrowDown from "@/template_full/icons/nexture/ni-arrow-down";
import NiArrowInDown from "@/template_full/icons/nexture/ni-arrow-in-down";
import NiArrowUp from "@/template_full/icons/nexture/ni-arrow-up";
import NiBinEmpty from "@/template_full/icons/nexture/ni-bin-empty";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftRightSmall from "@/template_full/icons/nexture/ni-chevron-left-right-small";
import NiCols from "@/template_full/icons/nexture/ni-cols";
import NiCross from "@/template_full/icons/nexture/ni-cross";
import NiEllipsisVertical from "@/template_full/icons/nexture/ni-ellipsis-vertical";
import NiEyeInactive from "@/template_full/icons/nexture/ni-eye-inactive";
import NiFilter from "@/template_full/icons/nexture/ni-filter";
import NiFilterPlus from "@/template_full/icons/nexture/ni-filter-plus";
import NiPlus from "@/template_full/icons/nexture/ni-plus";
import NiPushPinLeft from "@/template_full/icons/nexture/ni-push-pin-left";
import NiPushPinRight from "@/template_full/icons/nexture/ni-push-pin-right";
import NiSearch from "@/template_full/icons/nexture/ni-search";

dayjs.extend(duration);
dayjs.extend(relativeTime);

export default function OrderDetailInfo() {
  function GridCustomToolbar() {
    return (
      <Toolbar className="flex flex-row items-center">
        <Typography variant="h5" component="h5" className="card-title flex-1">
          Order Detail
        </Typography>
        <QuickFilter expanded>
          <QuickFilterControl
            render={({ ref, ...other }) => (
              <TextField
                {...other}
                inputRef={ref}
                aria-label="Search"
                placeholder="Search..."
                variant="standard"
                className="outlined mr-0.25 max-w-80"
                size="small"
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <NiSearch />
                      </InputAdornment>
                    ),
                    endAdornment: other.value ? (
                      <InputAdornment position="end">
                        <QuickFilterClear edge="end" size="small">
                          <NiCross />
                        </QuickFilterClear>
                      </InputAdornment>
                    ) : null,
                    ...other.slotProps?.input,
                  },
                  ...other.slotProps,
                }}
              />
            )}
          />
        </QuickFilter>
      </Toolbar>
    );
  }

  return (
    <Card className="mb-5">
      <CardContent>
        <Box className="mb-4">
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
            }}
          />
        </Box>

        <Box className="ml-auto flex max-w-xs flex-col gap-3 px-2">
          <Box className="flex flex-row justify-between">
            <Typography variant="subtitle1">Subtotal</Typography>
            <Typography>$342.35</Typography>
          </Box>

          <Box className="flex flex-row justify-between">
            <Typography variant="subtitle1">Tax</Typography>
            <Typography>$25.50</Typography>
          </Box>

          <Box className="flex flex-row justify-between">
            <Typography variant="subtitle1">Discount</Typography>
            <Typography>-$65.20</Typography>
          </Box>

          <Box className="flex flex-row justify-between">
            <Typography variant="subtitle1">Grand Total</Typography>
            <Typography>$302.65</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

const columns: GridColDef<(typeof rows)[number]>[] = [
  {
    field: "image",
    headerName: "Image",
    width: 90,
    editable: false,
    filterable: false,
    renderCell: (params: GridRenderCellParams<any, string>) => (
      <Box className="flex h-full items-center">
        <img src={params.value as string} alt="grid image" className="h-9 w-12 rounded-sm object-cover" />
      </Box>
    ),
  },
  { field: "id", headerName: "ID", width: 100 },
  {
    field: "name",
    headerName: "Name",
    width: 200,
    renderCell: (params: GridRenderCellParams<any, string>) => (
      <Link href="#" variant="body1" underline="hover" className="text-text-primary">
        {params.value}
      </Link>
    ),
  },
  {
    field: "price",
    headerName: "Price",
    type: "number",
    width: 170,
    align: "left",
    headerAlign: "left",
    valueFormatter: (value) => {
      if (!value) {
        return value;
      }
      return currencyFormatter.format(value);
    },
  },
  {
    field: "quantity",
    headerName: "Quantity",
    align: "left",
    headerAlign: "left",
    width: 200,
    type: "number",
  },
  {
    field: "total",
    headerName: "Total",
    align: "right",
    headerAlign: "right",
    flex: 1,
    type: "number",
    renderCell: (params: GridRenderCellParams<any, number>) =>
      currencyFormatter.format(params.row.quantity * params.row.price),
  },
];

const rows = [
  {
    id: 472,
    image: "/images/products/product-1.jpg",
    name: "Woolworth",
    price: 17.84,
    quantity: 2,
  },
  {
    id: 473,
    image: "/images/products/product-2.jpg",
    name: "Subwoofer",
    price: 5.22,
    quantity: 1,
  },
  {
    id: 474,
    image: "/images/products/product-3.jpg",
    name: "Dodo",
    price: 6.48,
    quantity: 1,
  },
  {
    id: 475,
    image: "/images/products/product-4.jpg",
    name: "Stretchy",
    price: 14.26,
    quantity: 4,
  },
  {
    id: 476,
    image: "/images/products/product-5.jpg",
    name: "Pony Soprano",
    price: 8.64,
    quantity: 1,
  },
  {
    id: 477,
    image: "/images/products/product-6.jpg",
    name: "Buck Rogers",
    price: 8.84,
    quantity: 1,
  },
];

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

