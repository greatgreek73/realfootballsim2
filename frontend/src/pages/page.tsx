import { useEffect, useState } from "react";
import { Box, Paper, Typography, Divider } from "@mui/material";
import { getJSON } from "@/lib/apiClient";

type ClubSummary = {
  id: number;
  name: string;
  country?: string;
  league?: string;
  status?: string;
  tokens?: number;
  money?: number;
};

export default function Page() {
  const [club, setClub] = useState<ClubSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const { id } = await getJSON<{ id: number }>("/api/my/club/");
        const summary = await getJSON<ClubSummary>(`/api/clubs/${id}/summary/`);
        setClub(summary);
      } catch (e: any) {
        setError(e?.message ?? "Failed to load club");
      }
    })();
  }, []);

  if (error) {
    return (
      <Box className="p-6">
        <Typography variant="h5">My Club</Typography>
        <Typography color="error" className="mt-2">{error}</Typography>
      </Box>
    );
  }

  if (!club) {
    return (
      <Box className="p-6">
        <Typography variant="h5">My Club</Typography>
        <Typography className="mt-2">Loading…</Typography>
      </Box>
    );
  }

  return (
    <Box className="p-6">
      <Typography variant="h5" className="mb-1">{club.name}</Typography>
      <Typography variant="body2" className="text-text-secondary mb-4">
        Country: {club.country || "—"} • League: {club.league || "—"} • {club.status || "—"}
      </Typography>

      <Box className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Paper className="p-4">
          <Typography variant="subtitle2">Your tokens</Typography>
          <Typography variant="h6">{club.tokens ?? 0}</Typography>
        </Paper>
        <Paper className="p-4">
          <Typography variant="subtitle2">Your money</Typography>
          <Typography variant="h6">{club.money ?? 0}</Typography>
        </Paper>
      </Box>

      <Divider className="my-6" />

      <Paper className="p-4">
        <Typography variant="subtitle1" className="mb-2">Players</Typography>
        <Typography variant="body2" className="text-text-secondary">
          (Здесь будет таблица игроков — подключим следующим шагом)
        </Typography>
      </Paper>
    </Box>
  );
}
