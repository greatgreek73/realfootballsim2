import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Avatar,
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  InputAdornment,
  Paper,
  Skeleton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  TextField,
  Typography,
} from "@mui/material";

// Fallback import if "@" alias not configured:
// import { getJSON } from "../../lib/apiClient";
import { getJSON } from "@/lib/apiClient";

type PlayerRow = {
  id: number;
  name: string;
  position: string;
  cls: string | number;
};

type Order = "asc" | "desc";

function initials(name: string) {
  const parts = name.split(" ").filter(Boolean);
  return (parts[0]?.[0] ?? "").toUpperCase() + (parts[1]?.[0] ?? "").toUpperCase();
}

function PositionChip({ value }: { value: string }) {
  const v = (value || "").toLowerCase();
  // Simple palette based on positions
  let color: "default" | "primary" | "secondary" | "success" | "warning" | "info" | "error" = "default";
  if (["goalkeeper"].includes(v)) color = "info";
  else if (["center back", "right back", "left back"].includes(v)) color = "secondary";
  else if (["central midfielder", "right midfielder", "left midfielder"].includes(v)) color = "primary";
  else if (["center forward"].includes(v)) color = "success";
  return <Chip size="small" color={color} variant="outlined" label={value || "-"} />;
}

function ClassChip({ value }: { value: string | number }) {
  return <Chip size="small" color="default" variant="outlined" label={`Class ${value ?? "-"}`} />;
}

// Sorting utilities
function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
  const av = String(a[orderBy] ?? "").toLowerCase();
  const bv = String(b[orderBy] ?? "").toLowerCase();
  if (bv < av) return -1;
  if (bv > av) return 1;
  return 0;
}

function getComparator<Key extends keyof any>(
  order: Order,
  orderBy: Key
): (a: { [key in Key]: unknown }, b: { [key in Key]: unknown }) => number {
  return order === "desc"
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

export default function ClubPlayersTable() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<PlayerRow[]>([]);

  const [query, setQuery] = useState("");
  const [order, setOrder] = useState<Order>("asc");
  const [orderBy, setOrderBy] = useState<keyof PlayerRow>("name");

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setError(null);
        setLoading(true);

        // 1) Get current user's club ID
        const my = await getJSON<{ id: number }>("/api/my/club/");
        // 2) Load players
        const players = await getJSON<{ count: number; results: PlayerRow[] }>(`/api/clubs/${my.id}/players/`);

        if (!cancelled) {
          setRows(players.results || []);
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
  }, []);

  const filtered = useMemo(() => {
    if (!query) return rows;
    const q = query.toLowerCase();
    return rows.filter((r) => (r.name || "").toLowerCase().includes(q) || (r.position || "").toLowerCase().includes(q));
  }, [rows, query]);

  const sorted = useMemo(() => {
    const cmp = getComparator(order, orderBy);
    return [...filtered].sort(cmp);
  }, [filtered, order, orderBy]);

  const paged = useMemo(() => {
    const start = page * rowsPerPage;
    return sorted.slice(start, start + rowsPerPage);
  }, [sorted, page, rowsPerPage]);

  const handleRequestSort = (_: unknown, property: keyof PlayerRow) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const empty = !loading && !error && rows.length === 0;

  return (
    <Card>
      <CardHeader
        title={<Typography variant="subtitle1">Players</Typography>}
        action={
          <TextField
            size="small"
            placeholder="Search players…"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setPage(0);
            }}
            InputProps={{
              startAdornment: <InputAdornment position="start">🔎</InputAdornment>,
            }}
          />
        }
      />
      <Divider />

      {/* Error state */}
      {error && (
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      )}

      <CardContent sx={{ pt: 0 }}>
        {loading ? (
          // Loading state with skeletons
          <Stack spacing={1} className="p-2">
            <Skeleton height={36} />
            <Skeleton height={36} />
            <Skeleton height={36} />
          </Stack>
        ) : empty ? (
          // Empty state
          <Paper variant="outlined" className="p-3">
            <Typography variant="body2">No players found in the club.</Typography>
          </Paper>
        ) : (
          // Table with data
          <>
            <TableContainer>
              <Table size="small" aria-label="players">
                <TableHead>
                  <TableRow>
                    <TableCell sortDirection={orderBy === "id" ? order : false}>
                      <TableSortLabel
                        active={orderBy === "id"}
                        direction={orderBy === "id" ? order : "asc"}
                        onClick={(e) => handleRequestSort(e, "id")}
                      >
                        ID
                      </TableSortLabel>
                    </TableCell>
                    <TableCell sortDirection={orderBy === "name" ? order : false}>
                      <TableSortLabel
                        active={orderBy === "name"}
                        direction={orderBy === "name" ? order : "asc"}
                        onClick={(e) => handleRequestSort(e, "name")}
                      >
                        Name
                      </TableSortLabel>
                    </TableCell>
                    <TableCell sortDirection={orderBy === "position" ? order : false}>
                      <TableSortLabel
                        active={orderBy === "position"}
                        direction={orderBy === "position" ? order : "asc"}
                        onClick={(e) => handleRequestSort(e, "position")}
                      >
                        Position
                      </TableSortLabel>
                    </TableCell>
                    <TableCell align="left">Class</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {paged.map((r) => (
                    <TableRow hover key={r.id}>
                      <TableCell width={80}>
                        <Typography variant="body2" color="text.secondary">
                          {r.id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Avatar sx={{ width: 28, height: 28 }}>{initials(r.name)}</Avatar>
                          <Typography variant="body2">{r.name}</Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <PositionChip value={r.position} />
                      </TableCell>
                      <TableCell>
                        <ClassChip value={r.cls} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              component="div"
              count={sorted.length}
              page={page}
              onPageChange={(_, p) => setPage(p)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </>
        )}
      </CardContent>
    </Card>
  );
}