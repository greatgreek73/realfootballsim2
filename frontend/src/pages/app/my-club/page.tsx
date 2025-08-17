import React, { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Divider,
  Grid,
  Paper,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

type MyClubResp = { id: number };
type ClubSummary = {
  id: number;
  name: string;
  country: string;
  league: string;
  status: string;
  tokens: number;
  money: number;
};
type PlayerRow = { id: number; name: string; position: string; cls: string | number | null };
type PlayersResp = { count: number; results: PlayerRow[] };

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`.slice(0, 300));
  }
  return res.json() as Promise<T>;
}

export default function Page() {
  const [clubId, setClubId] = useState<number | null>(null);
  const [summary, setSummary] = useState<ClubSummary | null>(null);
  const [players, setPlayers] = useState<PlayerRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setError(null);
        const { id } = await getJSON<MyClubResp>("/api/my/club/");
        if (!alive) return;
        setClubId(id);

        const [s, p] = await Promise.all([
          getJSON<ClubSummary>(`/api/clubs/${id}/summary/`),
          getJSON<PlayersResp>(`/api/clubs/${id}/players/`),
        ]);
        if (!alive) return;
        setSummary(s);
        setPlayers(p.results);
      } catch (e: any) {
        if (!alive) return;
        setError(e?.message ?? "Failed to load club data");
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const loading = !error && (clubId === null || !summary || !players);

  return (
    <Box className="p-6">
      <Typography variant="h5" className="mb-4">
        {summary ? `My Club — ${summary.name}` : "My Club"}
      </Typography>

      {error && (
        <Alert severity="error" className="mb-4">
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper className="p-4">
            {loading ? (
              <>
                <Skeleton width={240} height={28} />
                <Skeleton width="100%" height={20} />
                <Skeleton width="60%" height={20} />
              </>
            ) : summary ? (
              <>
                <Typography variant="subtitle1" className="mb-2">
                  Summary
                </Typography>
                <Divider className="mb-3" />
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6} lg={3}>
                    <Typography variant="body2" className="text-text-secondary">
                      Country
                    </Typography>
                    <Typography variant="h6">{summary.country || "—"}</Typography>
                  </Grid>
                  <Grid item xs={12} md={6} lg={3}>
                    <Typography variant="body2" className="text-text-secondary">
                      League
                    </Typography>
                    <Typography variant="h6">{summary.league || "—"}</Typography>
                  </Grid>
                  <Grid item xs={12} md={6} lg={3}>
                    <Typography variant="body2" className="text-text-secondary">
                      Tokens
                    </Typography>
                    <Typography variant="h6">{summary.tokens ?? 0}</Typography>
                  </Grid>
                  <Grid item xs={12} md={6} lg={3}>
                    <Typography variant="body2" className="text-text-secondary">
                      Money
                    </Typography>
                    <Typography variant="h6">{summary.money ?? 0}</Typography>
                  </Grid>
                </Grid>
                <Typography variant="body2" className="mt-2 text-text-secondary">
                  {summary.status}
                </Typography>
              </>
            ) : (
              <Typography>Нет данных о клубе.</Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper className="p-4">
            <Typography variant="subtitle1" className="mb-2">
              Players
            </Typography>
            <Divider className="mb-3" />
            {loading ? (
              <>
                <Skeleton width="100%" height={36} />
                <Skeleton width="100%" height={36} />
                <Skeleton width="100%" height={36} />
              </>
            ) : players && players.length ? (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Position</TableCell>
                    <TableCell>Class</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {players.map((p) => (
                    <TableRow key={p.id}>
                      <TableCell>{p.id}</TableCell>
                      <TableCell>{p.name}</TableCell>
                      <TableCell>{p.position || "—"}</TableCell>
                      <TableCell>{String(p.cls ?? "")}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <Typography>В клубе пока нет игроков.</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
