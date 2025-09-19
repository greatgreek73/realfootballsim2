import { useMemo } from "react";
import { Avatar, Box, Chip, Typography } from "@mui/material";
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridRowSpacingParams,
} from "@mui/x-data-grid";

import SquadToolbar from "./SquadToolbar";
import { DataGridPaginationFullPage } from "@/components/data-grid/data-grid-pagination";

export type SquadRow = {
  id: number;
  name: string;
  avatarUrl?: string | null;
  position: string;
  classLabel?: string | number;
  age?: number;
  morale?: number;
  status?: string;
  updatedAt?: string;
};

type ChipColor = "default" | "primary" | "secondary" | "success" | "warning" | "info" | "error";

const STATUS_COLOR: Record<string, ChipColor> = {
  healthy: "success",
  injured: "error",
  training: "info",
  resting: "warning",
  blooming: "primary",
};

const POSITION_COLOR_MAP: Record<string, ChipColor> = {
  goalkeeper: "info",
  back: "secondary",
  defender: "secondary",
  midfielder: "primary",
  forward: "success",
};

const getPositionChipColor = (position: string): ChipColor => {
  const key = position.toLowerCase();
  const match = Object.keys(POSITION_COLOR_MAP).find((pattern) => key.includes(pattern));
  return match ? POSITION_COLOR_MAP[match] : "default";
};

const getRowSpacing = (params: GridRowSpacingParams) => {
  if (params.isFirstVisible) {
    return { top: 0, bottom: 8 };
  }

  return { top: 8, bottom: 8 };
};

const formatNumber = (value: number | undefined) => (value !== undefined && value !== null ? String(value) : "-");
const formatText = (value: string | undefined | null) => (value ? value : "-");

const columns: GridColDef<SquadRow>[] = [
  {
    field: "id",
    headerName: "ID",
    width: 120,
    renderCell: (params: GridRenderCellParams<SquadRow, number>) => (
      <Typography variant="body2" color="text.secondary">
        #{params.value}
      </Typography>
    ),
  },
  {
    field: "name",
    headerName: "Player",
    flex: 1,
    minWidth: 220,
    renderCell: (params: GridRenderCellParams<SquadRow, string>) => {
      const name = params.value ?? "Unknown";
      const avatarUrl = params.row.avatarUrl ?? undefined;

      return (
        <Box className="flex h-full items-center gap-2">
          <Avatar src={avatarUrl} alt={name} sx={{ width: 32, height: 32 }}>
            {initials(name)}
          </Avatar>
          <Typography variant="body1" component="div">
            {name}
          </Typography>
        </Box>
      );
    },
  },
  {
    field: "position",
    headerName: "Position",
    width: 160,
    renderCell: (params: GridRenderCellParams<SquadRow, string>) => {
      const value = params.value ?? "-";
      const color = value ? getPositionChipColor(value) : "default";
      return <Chip size="small" variant="outlined" color={color} label={value} />;
    },
  },
  {
    field: "classLabel",
    headerName: "Class",
    width: 120,
    renderCell: (params: GridRenderCellParams<SquadRow, string | number>) => (
      <Chip size="small" variant="outlined" label={`Class ${params.value ?? "-"}`} />
    ),
  },
  {
    field: "age",
    headerName: "Age",
    width: 100,
    align: "center",
    headerAlign: "center",
    valueFormatter: (value) => formatNumber(value as number | undefined),
  },
  {
    field: "morale",
    headerName: "Morale",
    width: 140,
    valueFormatter: (value) => formatNumber(value as number | undefined),
  },
  {
    field: "status",
    headerName: "Status",
    width: 180,
    renderCell: (params: GridRenderCellParams<SquadRow, string>) => {
      const status = (params.value ?? "").toLowerCase();
      const color = STATUS_COLOR[status] ?? "default";
      const label = params.value ?? "Active";
      return <Chip size="small" label={label} color={color} variant={color === "default" ? "outlined" : "filled"} />;
    },
  },
  {
    field: "updatedAt",
    headerName: "Updated",
    width: 180,
    valueFormatter: (value) => formatText(value as string | undefined | null),
  },
];

function initials(name: string): string {
  const parts = name.split(" ").filter(Boolean);
  return (parts[0]?.[0] ?? "").toUpperCase() + (parts[1]?.[0] ?? "").toUpperCase();
}

type SquadDataGridProps = {
  rows: SquadRow[];
  loading?: boolean;
  pageSize?: number;
};

export default function SquadDataGrid({ rows, loading = false, pageSize = 10 }: SquadDataGridProps) {
  const paginationModel = useMemo(() => ({ pageSize, page: 0 }), [pageSize]);

  return (
    <DataGrid
      autoHeight
      rows={rows}
      columns={columns}
      loading={loading}
      checkboxSelection
      disableRowSelectionOnClick
      pagination
      rowHeight={68}
      columnHeaderHeight={36}
      initialState={{
        pagination: {
          paginationModel,
        },
      }}
      getRowSpacing={getRowSpacing}
      className="full-page border-none"
      pageSizeOptions={[10, 25, 50]}
      slots={{
        toolbar: SquadToolbar,
        basePagination: DataGridPaginationFullPage,
      }}
      slotProps={{
        basePagination: {
          labelRowsPerPage: "Rows per page",
        },
      }}
      hideFooterSelectedRowCount
      showCellVerticalBorder={false}
      showColumnVerticalBorder={false}
    />
  );
}
