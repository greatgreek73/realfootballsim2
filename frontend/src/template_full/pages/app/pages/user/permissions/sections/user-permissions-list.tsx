import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import relativeTime from "dayjs/plugin/relativeTime";
import { useCallback, useState } from "react";

import {
  Box,
  Button,
  FilledInput,
  FormControl,
  IconButton,
  InputAdornment,
  InputLabel,
  Select,
  SelectProps,
} from "@mui/material";
import { Grid } from "@mui/material";
import { GridColDef, GridRenderEditCellParams } from "@mui/x-data-grid";
import {
  GridActionsCellItem,
  GridRenderCellParams,
  GridRowSelectionModel,
  GridRowSpacingParams,
  QuickFilter,
  QuickFilterClear,
  QuickFilterControl,
  Toolbar,
} from "@mui/x-data-grid";
import { DataGridPro } from "@mui/x-data-grid-pro";

import DataGridSelect from "@/template_full/components/data-grid/data-grid-select";
import NiArrowDown from "@/template_full/icons/nexture/ni-arrow-down";
import NiArrowUp from "@/template_full/icons/nexture/ni-arrow-up";
import NiBinEmpty from "@/template_full/icons/nexture/ni-bin-empty";
import NiCheckSquare from "@/template_full/icons/nexture/ni-check-square";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftRightSmall from "@/template_full/icons/nexture/ni-chevron-left-right-small";
import NiCols from "@/template_full/icons/nexture/ni-cols";
import NiCross from "@/template_full/icons/nexture/ni-cross";
import NiCrossSquare from "@/template_full/icons/nexture/ni-cross-square";
import NiDuplicate from "@/template_full/icons/nexture/ni-duplicate";
import NiEllipsisVertical from "@/template_full/icons/nexture/ni-ellipsis-vertical";
import NiEyeInactive from "@/template_full/icons/nexture/ni-eye-inactive";
import NiFilter from "@/template_full/icons/nexture/ni-filter";
import NiFilterPlus from "@/template_full/icons/nexture/ni-filter-plus";
import NiPenSquare from "@/template_full/icons/nexture/ni-pen-square";
import NiSearch from "@/template_full/icons/nexture/ni-search";
import { cn } from "@/template_full/lib/utils";

const initialRows = [
  {
    id: crypto.randomUUID(),
    type: "Product",
    configuration: "All Current and Future Items",
    view: true,
    create: true,
    edit: true,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Category",
    configuration: "All Current and Future Items",
    view: true,
    create: true,
    edit: true,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Discount",
    configuration: "All Current and Future Items",
    view: true,
    create: true,
    edit: true,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "User",
    configuration: "All Current and Future Items",
    view: true,
    create: true,
    edit: true,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Team",
    configuration: "All Current and Future Items",
    view: true,
    create: true,
    edit: true,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Project",
    configuration: "All Current and Future Items",
    view: true,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Issue",
    configuration: "All Current and Future Items",
    view: true,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Invoice",
    configuration: "All Current and Future Items",
    view: true,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Post",
    configuration: "All Current and Future Items",
    view: false,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Page",
    configuration: "All Current and Future Items",
    view: false,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Tutorial",
    configuration: "All Current and Future Items",
    view: false,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Article",
    configuration: "All Current and Future Items",
    view: false,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Image",
    configuration: "All Current and Future Items",
    view: false,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Video",
    configuration: "All Current and Future Items",
    view: false,
    create: false,
    edit: false,
    delete: false,
  },
  {
    id: crypto.randomUUID(),
    type: "Brand",
    configuration: "All Current and Future Items",
    view: false,
    create: false,
    edit: false,
    delete: false,
  },
];

type Row = (typeof initialRows)[number];
dayjs.extend(duration);
dayjs.extend(relativeTime);

export default function UserPermissionsList() {
  const [rowSelectionModel, setRowSelectionModel] = useState<GridRowSelectionModel>({
    type: "include",
    ids: new Set(),
  });

  const getRowSpacing = useCallback((params: GridRowSpacingParams) => {
    return {
      top: params.isFirstVisible ? 0 : 5,
      bottom: 5,
    };
  }, []);

  const [rows] = useState<Row[]>(initialRows);

  const columns: GridColDef<(typeof rows)[number]>[] = [
    {
      field: "id",
      headerName: "ID",
      width: 240,
      type: "string",
    },
    {
      field: "type",
      headerName: "Type",
      align: "left",
      headerAlign: "left",
      type: "singleSelect",
      width: 140,
      valueOptions: [
        "Product",
        "Category",
        "Discount",
        "User",
        "Team",
        "Project",
        "Issue",
        "Invoice",
        "Post",
        "Page",
        "Tutorial",
        "Article",
        "Image",
        "Video",
        "Brand",
        "Order",
        "Customer",
      ],
      editable: true,
      renderEditCell: (params: GridRenderEditCellParams) => <DataGridSelect {...params} />,
    },
    {
      field: "configuration",
      headerName: "Configuration",
      align: "left",
      headerAlign: "left",
      type: "singleSelect",
      width: 240,
      valueOptions: ["All Current Items", "All Future Items", "All Current and Future Items"],
      editable: true,
      renderEditCell: (params: GridRenderEditCellParams) => <DataGridSelect {...params} />,
    },
    {
      field: "view",
      headerName: "View",
      align: "left",
      headerAlign: "left",
      type: "boolean",
      width: 100,
      editable: true,
      renderCell: (params: GridRenderCellParams<any, boolean>) => {
        const value = params.value;
        if (typeof value !== "undefined") {
          return value ? <NiCheckSquare className="text-success" /> : <NiCrossSquare className="text-error" />;
        } else {
          return <Box></Box>;
        }
      },
    },
    {
      field: "create",
      headerName: "Create",
      align: "left",
      headerAlign: "left",
      type: "boolean",
      width: 100,
      editable: true,
      renderCell: (params: GridRenderCellParams<any, boolean>) => {
        const value = params.value;
        if (typeof value !== "undefined") {
          return value ? <NiCheckSquare className="text-success" /> : <NiCrossSquare className="text-error" />;
        } else {
          return <Box></Box>;
        }
      },
    },
    {
      field: "edit",
      headerName: "Edit",
      align: "left",
      headerAlign: "left",
      type: "boolean",
      width: 100,
      editable: true,
      renderCell: (params: GridRenderCellParams<any, boolean>) => {
        const value = params.value;
        if (typeof value !== "undefined") {
          return value ? <NiCheckSquare className="text-success" /> : <NiCrossSquare className="text-error" />;
        } else {
          return <Box></Box>;
        }
      },
    },
    {
      field: "delete",
      headerName: "Delete",
      align: "left",
      headerAlign: "left",
      type: "boolean",
      width: 100,
      editable: true,
      renderCell: (params: GridRenderCellParams<any, boolean>) => {
        const value = params.value;
        if (typeof value !== "undefined") {
          return value ? <NiCheckSquare className="text-success" /> : <NiCrossSquare className="text-error" />;
        } else {
          return <Box></Box>;
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
        <GridActionsCellItem key={1} icon={<NiPenSquare size="medium" />} label="Edit" showInMenu />,
        <GridActionsCellItem key={2} icon={<NiDuplicate size="medium" />} label="Duplicate" showInMenu />,
        <GridActionsCellItem key={0} icon={<NiCrossSquare size="medium" />} label="Delete" showInMenu />,
      ],
    },
  ];

  function CustomToolbar() {
    return (
      <Toolbar className="min-h-auto border-none">
        <Grid container spacing={5} className="mb-4 w-full">
          <FormControl variant="filled" size="medium" className="surface mb-0 flex-1 pt-0.25">
            <InputLabel>Search</InputLabel>
            <QuickFilter
              render={() => (
                <QuickFilterControl
                  render={({ ref, ...controlProps }, state) => (
                    <FilledInput
                      {...controlProps}
                      inputRef={ref}
                      endAdornment={
                        <>
                          <InputAdornment position="end" className={cn(state.value === "" && "hidden")}>
                            <QuickFilterClear edge="end">
                              <NiCross size="medium" className="text-text-disabled" />
                            </QuickFilterClear>
                          </InputAdornment>
                          <InputAdornment position="end" className={cn(state.value !== "" && "hidden")}>
                            <IconButton edge="end">
                              {<NiSearch size="medium" className="text-text-disabled" />}
                            </IconButton>
                          </InputAdornment>
                        </>
                      }
                    />
                  )}
                />
              )}
            />
          </FormControl>
        </Grid>
      </Toolbar>
    );
  }

  return (
    <DataGridPro
      rows={rows}
      columns={columns}
      initialState={{
        columns: { columnVisibilityModel: { id: false } },
      }}
      pagination={false}
      hideFooter
      getRowSpacing={getRowSpacing}
      rowHeight={68}
      columnHeaderHeight={32}
      disableRowSelectionOnClick
      pageSizeOptions={[10]}
      className="full-page border-none"
      slotProps={{
        panel: {
          className: "mt-1!",
        },
      }}
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
        filterPanelDeleteIcon: NiCross,
        filterPanelRemoveAllIcon: NiBinEmpty,
        baseSelect: (props: any) => {
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
        toolbar: CustomToolbar,
      }}
      rowSelectionModel={rowSelectionModel}
      onRowSelectionModelChange={(rowSelectionModel: GridRowSelectionModel) => {
        setRowSelectionModel(rowSelectionModel);
      }}
      hideFooterSelectedRowCount
      showToolbar
    />
  );
}

