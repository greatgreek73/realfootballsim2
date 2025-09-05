import { Box, Button, FormControl, InputLabel, Select, SelectProps } from "@mui/material";
import { DataGridPremium, GridColDef, GridInitialState, GridPivotModel, GridRowModel } from "@mui/x-data-grid-premium";

import NiArrowDown from "@/template_full/icons/nexture/ni-arrow-down";
import NiArrowInDown from "@/template_full/icons/nexture/ni-arrow-in-down";
import NiArrowUp from "@/template_full/icons/nexture/ni-arrow-up";
import NiBinEmpty from "@/template_full/icons/nexture/ni-bin-empty";
import NiCheck from "@/template_full/icons/nexture/ni-check";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftRightSmall from "@/template_full/icons/nexture/ni-chevron-left-right-small";
import NiChevronUpSmall from "@/template_full/icons/nexture/ni-chevron-up-small";
import NiCols from "@/template_full/icons/nexture/ni-cols";
import NiCross from "@/template_full/icons/nexture/ni-cross";
import NiEllipsisVertical from "@/template_full/icons/nexture/ni-ellipsis-vertical";
import NiEndDownSmall from "@/template_full/icons/nexture/ni-end-down-small";
import NiEndUpSmall from "@/template_full/icons/nexture/ni-end-up-small";
import NiEyeInactive from "@/template_full/icons/nexture/ni-eye-inactive";
import NiFilter from "@/template_full/icons/nexture/ni-filter";
import NiFilterPlus from "@/template_full/icons/nexture/ni-filter-plus";
import NiGroup from "@/template_full/icons/nexture/ni-group";
import NiPivot from "@/template_full/icons/nexture/ni-pivot";
import NiPlus from "@/template_full/icons/nexture/ni-plus";
import NiPushPinLeft from "@/template_full/icons/nexture/ni-push-pin-left";
import NiPushPinRight from "@/template_full/icons/nexture/ni-push-pin-right";
import NiSearch from "@/template_full/icons/nexture/ni-search";
import NiSum from "@/template_full/icons/nexture/ni-sum";
import NiUngroup from "@/template_full/icons/nexture/ni-ungroup";

const rows: GridRowModel[] = [
  {
    id: 1,
    product: "Apples",
    region: "North",
    quarter: "Q1",
    sales: 1000,
    profit: 100,
    size: "L",
  },
  {
    id: 2,
    product: "Apples",
    region: "South",
    quarter: "Q1",
    sales: 1200,
    profit: 120,
    size: "M",
  },
  {
    id: 3,
    product: "Oranges",
    region: "North",
    quarter: "Q1",
    sales: 800,
    profit: 80,
    size: "M",
  },
  {
    id: 4,
    product: "Oranges",
    region: "South",
    quarter: "Q1",
    sales: 900,
    profit: 90,
    size: "S",
  },
  {
    id: 5,
    product: "Apples",
    region: "North",
    quarter: "Q2",
    sales: 1100,
    profit: 110,
    size: "L",
  },
  {
    id: 6,
    product: "Apples",
    region: "South",
    quarter: "Q2",
    sales: 1300,
    profit: 130,
    size: "L",
  },
  {
    id: 7,
    product: "Oranges",
    region: "North",
    quarter: "Q2",
    sales: 850,
    profit: 85,
    size: "M",
  },
  {
    id: 8,
    product: "Oranges",
    region: "South",
    quarter: "Q2",
    sales: 950,
    profit: 95,
    size: "S",
  },
];

const columns: GridColDef[] = [
  { field: "product", headerName: "Product" },
  { field: "region", headerName: "Region" },
  { field: "quarter", headerName: "Quarter" },
  {
    field: "sales",
    headerName: "Sales",
    type: "number",
    valueFormatter: (value) => {
      if (!value) {
        return "";
      }
      return currencyFormatter.format(value);
    },
  },
  {
    field: "profit",
    headerName: "Profit",
    type: "number",
    valueFormatter: (value) => {
      if (!value) {
        return "";
      }
      return `${value}%`;
    },
  },
  {
    field: "size",
    headerName: "Size",
  },
];

const pivotModel: GridPivotModel = {
  rows: [{ field: "product" }, { field: "size" }],
  columns: [{ field: "region" }, { field: "quarter" }],
  values: [
    { field: "sales", aggFunc: "sum" },
    { field: "profit", aggFunc: "avg" },
  ],
};

const initialState: GridInitialState = {
  pivoting: {
    enabled: true,
    model: pivotModel,
    panelOpen: true,
  },
};

export default function PivotingBasic() {
  return (
    <Box className="h-[560px] w-full">
      <DataGridPremium
        rows={rows}
        columns={columns}
        initialState={initialState}
        columnGroupHeaderHeight={36}
        showToolbar
        slotProps={{
          toolbar: {
            showQuickFilter: false,
          },
        }}
        hideFooter
        disableRowSelectionOnClick
        label="Basic"
        className="border-none"
        slots={{
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
          columnMenuAggregationIcon: NiSum,
          columnMenuGroupIcon: NiGroup,
          columnMenuUngroupIcon: NiUngroup,
          filterPanelDeleteIcon: NiCross,
          filterPanelAddIcon: NiPlus,
          filterPanelRemoveAllIcon: NiBinEmpty,
          pivotIcon: NiPivot,
          columnSelectorIcon: NiCols,
          exportIcon: NiArrowInDown,
          openFilterButtonIcon: NiFilter,
          collapsibleIcon: NiChevronDownSmall,
          pivotMenuAddIcon: () => {
            return <NiPlus size={"small"}></NiPlus>;
          },
          pivotMenuCheckIcon: () => {
            return <NiCheck size={"small"}></NiCheck>;
          },
          pivotMenuMoveDownIcon: () => {
            return <NiChevronDownSmall size={"small"}></NiChevronDownSmall>;
          },
          pivotMenuMoveUpIcon: () => {
            return <NiChevronUpSmall size={"small"}></NiChevronUpSmall>;
          },
          pivotMenuMoveToBottomIcon: () => {
            return <NiEndDownSmall size={"small"}></NiEndDownSmall>;
          },
          pivotMenuMoveToTopIcon: () => {
            return <NiEndUpSmall size={"small"}></NiEndUpSmall>;
          },
          pivotMenuRemoveIcon: () => {
            return <NiCross size={"small"}></NiCross>;
          },
          pivotSearchIcon: () => {
            return <NiSearch size={"small"}></NiSearch>;
          },
          pivotSearchClearIcon: () => {
            return <NiCross size={"medium"} />;
          },
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
  );
}

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

