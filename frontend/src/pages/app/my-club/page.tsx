import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  Grid,
  IconButton,
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
  Tooltip,
  Typography,
} from "@mui/material";

type ClubSummary = {
  id: number;
  name: string;
  country: string;
  league: string;
  status: string;
  tokens: number;
  money: number;
};

type PlayerRow = {
  id: number;
  name: string;
  position: string;
  cls: string | number;
};

type Order = "asc" | "desc";

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text.slice(0, 140)}`);
  }
  return res.json() as Promise<T>;
}

function initials(name: string) {
  const parts = name.split(" ").filter(Boolean);
  return (parts[0]?.[0] ?? "").toUpperCase() + (parts[1]?.[0] ?? "").toUpperCase();
}

function formatNumber(n: number) {
  try {
    return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(n);
  } catch {
    return String(n);
  }
}

function PositionChip({ value }: { value: string }) {
  const v = (value || "").toLowerCase();
  // простая палитра по позициям
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

// сортировка
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

export default function MyClubPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [club, setClub] = useState<ClubSummary | null>(null);
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

        // 1) узнаём club_id текущего пользователя
        const my = await getJSON<{ id: number }>("/api/my/club/");
        // 2) грузим сводку и игроков
        const [summary, players] = await Promise.all([
          getJSON<ClubSummary>(`/api/clubs/${my.id}/summary/`),
          getJSON<{ count: number; results: PlayerRow[] }>(`/api/clubs/${my.id}/players/`),
        ]);

        if (!cancelled) {
          setClub(summary);
          setRows(players.results || []);
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load");
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
    <Box className="p-2 sm:p-4">
      {/* Ошибка */}
      {error && (
        <Alert severity="error" className="mb-3">
          {error}
        </Alert>
      )}

      {/* Сводка + действия */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4} lg={3}>
          <Card>
            <CardHeader
              title={<Typography variant="subtitle1">Summary</Typography>}
              subheader={club?.name ? `My Club — ${club.name}` : "My Club"}
            />
            <CardContent>
              {loading ? (
                <Stack spacing={1}>
                  <Skeleton height={18} />
                  <Skeleton height={18} />
                  <Skeleton height={18} />
                  <Divider className="!my-1" />
                  <Skeleton height={30} />
                </Stack>
              ) : club ? (
                <Stack spacing={1}>
                  <Stack direction="row" spacing={2}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Country
                      </Typography>
                      <Typography variant="body2">{club.country || "-"}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        League
                      </Typography>
                      <Typography variant="body2">{club.league || "-"}</Typography>
                    </Box>
                  </Stack>

                  <Stack direction="row" spacing={1} className="mt-1">
                    <Chip label={`Tokens ${formatNumber(club.tokens)}`} size="small" color="primary" variant="outlined" />
                    <Chip label={`Money ${formatNumber(club.money)}`} size="small" color="success" variant="outlined" />
                  </Stack>

                  <Typography variant="caption" color="text.secondary" className="mt-1">
                    {club.status}
                  </Typography>
                </Stack>
              ) : (
                <Typography variant="body2">No data</Typography>
              )}
            </CardContent>
          </Card>

          <Box className="mt-3">
            <Card>
              <CardContent>
                <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                  <Typography variant="subtitle2">Actions</Typography>
                  <Tooltip title="Not implemented yet">
                    <span>
                      <Button size="small" variant="contained" disabled={loading || !club}>
                        Select Team Lineup
                      </Button>
                    </span>
                  </Tooltip>
                </Stack>
              </CardContent>
            </Card>
          </Box>
        </Grid>

        {/* Таблица игроков */}
        <Grid item xs={12} md={8} lg={9}>
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
            <CardContent sx={{ pt: 0 }}>
              {loading ? (
                <Stack spacing={1} className="p-2">
                  <Skeleton height={36} />
                  <Skeleton height={36} />
                  <Skeleton height={36} />
                </Stack>
              ) : empty ? (
                <Paper variant="outlined" className="p-3">
                  <Typography variant="body2">В клубе пока нет игроков.</Typography>
                </Paper>
              ) : (
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
        </Grid>
      </Grid>
    </Box>
  );
}
