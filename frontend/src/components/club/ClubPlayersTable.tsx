import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Card,
  CardContent,
  CardHeader,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Skeleton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import { SquadDataGrid, SquadRow } from "@/components/club/squad-table";
import { getJSON } from "@/lib/apiClient";

type ApiPlayer = {
  id: number;
  name: string;
  position: string;
  cls: string | number;
  age?: number;
  morale?: number;
  status?: string;
  updated_at?: string;
  avatar_url?: string | null;
  last_trained_at?: string | null;
};

function toSquadRow(player: ApiPlayer): SquadRow {
  return {
    id: player.id,
    name: player.name,
    avatarUrl: player.avatar_url ?? "/img/avatar-2.jpg",
    position: player.position,
    classLabel: player.cls,
    age: player.age,
    morale: player.morale,
    status: player.status ?? "Active",
    updatedAt: player.updated_at,
    lastTrainedAt: player.last_trained_at,
  };
}

type ClubPlayersTableProps = {
  refreshKey?: number;
};

export default function ClubPlayersTable({ refreshKey = 0 }: ClubPlayersTableProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<SquadRow[]>([]);
  const [search, setSearch] = useState("");
  const [positionFilter, setPositionFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [classFilter, setClassFilter] = useState<string>("all");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setError(null);
        setLoading(true);

        const my = await getJSON<{ id: number }>("/api/my/club/");
        // Отключаем кэш браузера, чтобы получать актуальные данные после тренировок
        const url = `/api/clubs/${my.id}/players/?_=${Date.now()}`;
        const res = await fetch(url, { credentials: "include", cache: "no-store" });
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
        const players = await res.json() as { count: number; results: ApiPlayer[] };

        if (!cancelled) {
          const transformed = (players.results ?? []).map(toSquadRow);
          if (transformed.length > 0) {
            // Debug: увидеть, что доходит до состояния
            console.log("[ClubPlayersTable] first row", {
              id: transformed[0]?.id,
              last_trained_at: players.results?.[0]?.last_trained_at,
              lastTrainedAt: transformed[0]?.lastTrainedAt,
            });
          }
          setRows(transformed);
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load players");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const empty = !loading && !error && rows.length === 0;
  const normalizedSearch = search.trim().toLowerCase();
  const filteredRows = useMemo(() => {
    return rows.filter((row) => {
      const matchesSearch =
        !normalizedSearch ||
        row.name?.toLowerCase().includes(normalizedSearch) ||
        String(row.id).includes(normalizedSearch) ||
        row.position?.toLowerCase().includes(normalizedSearch);
      const matchesPosition =
        positionFilter === "all" || row.position?.toLowerCase() === positionFilter.toLowerCase();
      const matchesStatus =
        statusFilter === "all" || (row.status ?? "active").toLowerCase() === statusFilter.toLowerCase();
      const matchesClass =
        classFilter === "all" ||
        String(row.classLabel ?? "")
          .toLowerCase()
          .includes(classFilter.toLowerCase());
      return matchesSearch && matchesPosition && matchesStatus && matchesClass;
    });
  }, [rows, normalizedSearch, positionFilter, statusFilter, classFilter]);

  const positionOptions = useMemo(() => {
    const unique = new Set<string>();
    rows.forEach((row) => {
      if (row.position) unique.add(row.position);
    });
    return Array.from(unique).sort((a, b) => a.localeCompare(b));
  }, [rows]);

  const statusOptions = useMemo(() => {
    const unique = new Set<string>();
    rows.forEach((row) => {
      if (row.status) unique.add(row.status);
    });
    return Array.from(unique).sort((a, b) => a.localeCompare(b));
  }, [rows]);
  const classOptions = useMemo(() => {
    const unique = new Set<string>();
    rows.forEach((row) => {
      if (row.classLabel !== undefined && row.classLabel !== null) {
        unique.add(String(row.classLabel));
      }
    });
    return Array.from(unique).sort((a, b) => a.localeCompare(b));
  }, [rows]);

  return (
    <Card>
      <CardHeader title={<Typography variant="subtitle1">Players</Typography>} subheader="Club Squad" />
      <Divider />

      {error && (
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      )}

      <CardContent sx={{ pt: 0 }}>
        {!loading && !error && (
          <>
            <Stack spacing={2} className="p-3">
              <TextField
                size="small"
                label="Search player"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
              <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                <FormControl size="small" sx={{ minWidth: 160 }}>
                  <InputLabel id="position-filter">Position</InputLabel>
                  <Select
                    labelId="position-filter"
                    value={positionFilter}
                    label="Position"
                    onChange={(event) => setPositionFilter(event.target.value)}
                  >
                    <MenuItem value="all">All positions</MenuItem>
                    {positionOptions.map((option) => (
                      <MenuItem key={option} value={option}>
                        {option}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 160 }}>
                  <InputLabel id="status-filter">Status</InputLabel>
                  <Select
                    labelId="status-filter"
                    value={statusFilter}
                    label="Status"
                    onChange={(event) => setStatusFilter(event.target.value)}
                  >
                    <MenuItem value="all">All statuses</MenuItem>
                    {statusOptions.map((option) => (
                      <MenuItem key={option} value={option}>
                        {option}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 160 }}>
                  <InputLabel id="class-filter">Class</InputLabel>
                  <Select
                    labelId="class-filter"
                    value={classFilter}
                    label="Class"
                    onChange={(event) => setClassFilter(event.target.value)}
                  >
                    <MenuItem value="all">All classes</MenuItem>
                    {classOptions.map((option) => (
                      <MenuItem key={option} value={option}>
                        {option}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Stack>
            </Stack>
            <Divider />
          </>
        )}

        {loading ? (
          <Stack spacing={1} className="p-2">
            <Skeleton height={36} />
            <Skeleton height={36} />
            <Skeleton height={36} />
          </Stack>
        ) : empty ? (
          <Paper variant="outlined" className="p-3">
            <Typography variant="body2">No players found in the club.</Typography>
          </Paper>
        ) : (
          <SquadDataGrid rows={filteredRows} loading={loading} />
        )}
      </CardContent>
    </Card>
  );
}
