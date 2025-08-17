import { useEffect, useMemo, useState } from "react";
import {
  Box, Paper, Typography, Grid, Table, TableBody, TableCell,
  TableHead, TableRow, Skeleton, Divider
} from "@mui/material";

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

type ClubSummary = {
  id: number; name: string; country?: string; league?: string;
  status?: string; tokens?: number; money?: number;
};
type PlayerRow = { id: number; name: string; position: string; cls: string | number };

export default function Page() {
  const [club, setClub] = useState<ClubSummary | null>(null);
  const [players, setPlayers] = useState<PlayerRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true); setErr(null);
        const { id } = await getJSON<{ id: number }>("/api/my/club/");
        const [summary, plist] = await Promise.all([
          getJSON<ClubSummary>(`/api/clubs/${id}/summary/`),
          getJSON<{ count: number; results: PlayerRow[] }>(`/api/clubs/${id}/players/`),
        ]);
        if (cancelled) return;
        setClub(summary);
        setPlayers(plist.results ?? []);
      } catch (e: any) {
        if (!cancelled) setErr(e?.message ?? "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const title = useMemo(() => club?.name ?? "My Club", [club?.name]);

  return (
    <Box className="p-6">
      <Typography variant="h5" className="mb-1">{title}</Typography>
      {loading ? (
        <Skeleton variant="text" width={280} />
      ) : (
        <Typography variant="body2" className="text-text-secondary mb-4">
          Country: {club?.country || "—"} • League: {club?.league || "—"} • {club?.status || "—"}
        </Typography>
      )}

      {err && <Paper className="p-4 mb-4"><Typography color="error">Error: {err}</Typography></Paper>}

      <Grid container spacing={2} className="mb-4">
        <Grid item xs={12} md={6} lg={3}>
          <Paper className="p-4">
            <Typography variant="subtitle2">Your tokens</Typography>
            {loading ? <Skeleton width={120} height={28} /> : <Typography variant="h6">{club?.tokens ?? 0}</Typography>}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Paper className="p-4">
            <Typography variant="subtitle2">Your money</Typography>
            {loading ? <Skeleton width={120} height={28} /> : <Typography variant="h6">{club?.money ?? 0}</Typography>}
          </Paper>
        </Grid>
      </Grid>

      <Divider className="my-4" />

      <Paper className="p-4">
        <Typography variant="subtitle1" className="mb-2">Players</Typography>
        {loading ? (
          <Box className="flex flex-col gap-2">
            <Skeleton variant="rectangular" height={36} />
            <Skeleton variant="rectangular" height={36} />
            <Skeleton variant="rectangular" height={36} />
          </Box>
        ) : players.length === 0 ? (
          <Typography variant="body2" className="text-text-secondary">No players found.</Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell style={{ width: 64 }}>ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Position</TableCell>
                <TableCell>Class</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {players.map(p => (
                <TableRow key={p.id}>
                  <TableCell>{p.id}</TableCell>
                  <TableCell>{p.name}</TableCell>
                  <TableCell>{p.position || "—"}</TableCell>
                  <TableCell>{p.cls || "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Paper>
    </Box>
  );
}