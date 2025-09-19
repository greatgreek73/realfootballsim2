import { useEffect, useState } from "react";
import { Alert, Card, CardContent, CardHeader, Divider, Paper, Skeleton, Stack, Typography } from "@mui/material";

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
};

function toSquadRow(player: ApiPlayer): SquadRow {
  return {
    id: player.id,
    name: player.name,
    avatarUrl: player.avatar_url ?? null,
    position: player.position,
    classLabel: player.cls,
    age: player.age,
    morale: player.morale,
    status: player.status ?? "Active",
    updatedAt: player.updated_at,
  };
}

export default function ClubPlayersTable() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<SquadRow[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setError(null);
        setLoading(true);

        const my = await getJSON<{ id: number }>("/api/my/club/");
        const players = await getJSON<{ count: number; results: ApiPlayer[] }>(`/api/clubs/${my.id}/players/`);

        if (!cancelled) {
          const transformed = (players.results ?? []).map(toSquadRow);
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
  }, []);

  const empty = !loading && !error && rows.length === 0;

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
          <SquadDataGrid rows={rows} loading={loading} />
        )}
      </CardContent>
    </Card>
  );
}
