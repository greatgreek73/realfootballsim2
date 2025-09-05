import { useEffect, useState } from "react";

import { Box, Button, FormControl, InputLabel, Select, SelectProps } from "@mui/material";
import { useDemoData } from "@mui/x-data-grid-generator";
import { DataGridPro, GridRowModel, GridRowOrderChangeParams } from "@mui/x-data-grid-pro";

import DataGridPagination from "@/template_full/components/data-grid/data-grid-pagination";
import NiArrowDown from "@/template_full/icons/nexture/ni-arrow-down";
import NiArrowInDown from "@/template_full/icons/nexture/ni-arrow-in-down";
import NiArrowUp from "@/template_full/icons/nexture/ni-arrow-up";
import NiBinEmpty from "@/template_full/icons/nexture/ni-bin-empty";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftRightSmall from "@/template_full/icons/nexture/ni-chevron-left-right-small";
import NiCols from "@/template_full/icons/nexture/ni-cols";
import NiCross from "@/template_full/icons/nexture/ni-cross";
import NiDragVertical from "@/template_full/icons/nexture/ni-drag-vertical";
import NiEllipsisVertical from "@/template_full/icons/nexture/ni-ellipsis-vertical";
import NiEyeInactive from "@/template_full/icons/nexture/ni-eye-inactive";
import NiFilter from "@/template_full/icons/nexture/ni-filter";
import NiFilterPlus from "@/template_full/icons/nexture/ni-filter-plus";
import NiPushPinLeft from "@/template_full/icons/nexture/ni-push-pin-left";
import NiPushPinRight from "@/template_full/icons/nexture/ni-push-pin-right";
import NiSearch from "@/template_full/icons/nexture/ni-search";

function updateRowPosition(initialIndex: number, newIndex: number, rows: GridRowModel[]): Promise<any> {
  return new Promise((resolve) => {
    setTimeout(
      () => {
        const rowsClone = [...rows];
        const row = rowsClone.splice(initialIndex, 1)[0];
        rowsClone.splice(newIndex, 0, row);
        resolve(rowsClone);
      },
      Math.random() * 500 + 100,
    ); // simulate network latency
  });
}

export default function RowReorderingBasic() {
  const { data, loading: initialLoadingState } = useDemoData({
    dataSet: "Commodity",
    rowLength: 10,
    maxColumns: 6,
  });

  const [rows, setRows] = useState(data.rows);
  const [loading, setLoading] = useState(initialLoadingState);

  useEffect(() => {
    setRows(data.rows);
  }, [data]);

  useEffect(() => {
    setLoading(initialLoadingState);
  }, [initialLoadingState]);

  const handleRowOrderChange = async (params: GridRowOrderChangeParams) => {
    setLoading(true);
    const newRows = await updateRowPosition(params.oldIndex, params.targetIndex, rows);

    setRows(newRows);
    setLoading(false);
  };

  return (
    <Box className="w-full">
      <DataGridPro
        {...data}
        loading={loading}
        rows={rows}
        rowReordering
        onRowOrderChange={handleRowOrderChange}
        className="border-none"
        disableRowSelectionOnClick
        slots={{
          basePagination: DataGridPagination,
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
          filterPanelDeleteIcon: NiCross,
          filterPanelRemoveAllIcon: NiBinEmpty,
          exportIcon: NiArrowInDown,
          columnSelectorIcon: NiCols,
          columnMenuPinLeftIcon: NiPushPinLeft,
          columnMenuPinRightIcon: NiPushPinRight,
          rowReorderIcon: NiDragVertical,
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

