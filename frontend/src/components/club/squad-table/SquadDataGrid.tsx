import { MouseEvent, useMemo, useState } from "react";
import { Avatar, Box, Chip, IconButton, Menu, MenuItem, Typography } from "@mui/material";
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridRowSpacingParams,
  GridValueFormatterParams,
} from "@mui/x-data-grid";
import { Link, useNavigate } from "react-router-dom";

import SquadToolbar from "./SquadToolbar";
import NiEllipsisVertical from "@/icons/nexture/ni-ellipsis-vertical";
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
  lastTrainedAt?: string | null;
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

const formatNumber = (value?: number | null) => (value !== undefined && value !== null ? String(value) : "-");
const formatNumberCell = (params?: GridValueFormatterParams<number | null>) => formatNumber(params?.value ?? null);
const formatDateTime = (value?: string | null) => {
  if (!value) return "-";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "-";
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
};

function initials(name: string): string {
  const parts = name.split(" ").filter(Boolean);
  return (parts[0]?.[0] ?? "").toUpperCase() + (parts[1]?.[0] ?? "").toUpperCase();
}

/** Меню действий по игроку в колонке "Actions" */
function PlayerActionsMenu({ playerId }: { playerId: number }) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const navigate = useNavigate();

  const handleOpen = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  /** Переход на нашу SPA‑страницу */
  const handleNavigateOverview = () => {
    navigate(`/player/overview?id=${playerId}`);
    handleClose();
  };

  /** Открыть старую Django‑страницу (на всякий случай оставить доступной) */
  const handleOpenLegacy = () => {
    const backendBase =
      import.meta.env.VITE_BACKEND_URL ?? (import.meta.env.DEV ? "http://127.0.0.1:8000" : window.location.origin);
    const normalizedBase = backendBase.endsWith("/") ? backendBase.slice(0, -1) : backendBase;
    window.open(`${normalizedBase}/players/detail/${playerId}/`, "_blank");
    handleClose();
  };

  return (
    <>
      <IconButton size="small" onClick={handleOpen} aria-label="Player actions">
        <NiEllipsisVertical size="medium" />
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        onClick={(event) => event.stopPropagation()}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        transformOrigin={{ vertical: "top", horizontal: "right" }}
      >
        <MenuItem onClick={handleNavigateOverview}>Overview</MenuItem>
        <MenuItem onClick={handleOpenLegacy}>Legacy profile (Django)</MenuItem>
      </Menu>
    </>
  );
}

/** Колонки грида */
const columns: GridColDef<SquadRow>[] = [
  {
    field: "id",
    headerName: "ID",
    width: 120,
    renderCell: (params: GridRenderCellParams<SquadRow, number>) => (
      <Typography variant="body2" color="text.secondary">#{params.value}</Typography>
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
          <Typography
            variant="body1"
            component={Link}
            to={`/player/overview?id=${params.row.id}`}
            className="no-underline hover:underline"
            onClick={(e) => e.stopPropagation()} // чтобы не дублировать onRowClick
          >
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
    align: "left",
    headerAlign: "left",
    valueFormatter: formatNumberCell,
  },
  {
    field: "morale",
    headerName: "Morale",
    width: 140,
    valueFormatter: formatNumberCell,
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
    field: "lastTrainedAt",
    headerName: "Last training",
    width: 160,
    valueFormatter: (params) => formatDateTime(params?.value as string | null),
  },
  {
    field: "actions",
    headerName: "Actions",
    width: 80,
    align: "right",
    headerAlign: "right",
    sortable: false,
    filterable: false,
    disableColumnMenu: true,
    renderCell: (params: GridRenderCellParams<SquadRow>) => <PlayerActionsMenu playerId={params.row.id} />,
  },
];

type SquadDataGridProps = {
  rows: SquadRow[];
  loading?: boolean;
  pageSize?: number;
};

export default function SquadDataGrid({ rows, loading = false, pageSize = 10 }: SquadDataGridProps) {
  const paginationModel = useMemo(() => ({ pageSize, page: 0 }), [pageSize]);
  const navigate = useNavigate();

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
      /** Переход по клику на строку */
      onRowClick={(params: any) => {
        const id = params?.row?.id ?? params?.id;
        if (id != null) navigate(`/player/overview?id=${id}`);
      }}
    />
  );
}
