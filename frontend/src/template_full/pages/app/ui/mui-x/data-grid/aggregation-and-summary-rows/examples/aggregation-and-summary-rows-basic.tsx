import { Button, FormControl, InputLabel, Select, SelectProps } from "@mui/material";
import { useMovieData } from "@mui/x-data-grid-generator";
import { DataGridPremium, GridColDef } from "@mui/x-data-grid-premium";

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

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

const COLUMNS: GridColDef[] = [
  { field: "title", headerName: "Title", width: 200, groupable: false },
  {
    field: "gross",
    headerName: "Gross",
    type: "number",
    width: 150,
    groupable: false,
    valueFormatter: (value) => {
      if (!value) {
        return value;
      }
      return currencyFormatter.format(value);
    },
  },
];

export default function AggregationAndSummaryRowsBasic() {
  const data = useMovieData();

  return (
    <div style={{ height: 400, width: "100%" }}>
      <DataGridPremium
        rows={data.rows}
        columns={COLUMNS}
        initialState={{
          aggregation: {
            model: {
              gross: "sum",
            },
          },
        }}
        disableRowSelectionOnClick
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
    </div>
  );
}

