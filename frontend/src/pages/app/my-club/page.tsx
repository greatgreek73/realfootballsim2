import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  Grid,
  Skeleton,
  Stack,
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


async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text.slice(0, 140)}`);
  }
  return res.json() as Promise<T>;
}

function formatNumber(n: number) {
  try {
    return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(n);
  } catch {
    return String(n);
  }
}

export default function MyClubPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [club, setClub] = useState<ClubSummary | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setError(null);
        setLoading(true);

        // 1) узнаём club_id текущего пользователя
        const my = await getJSON<{ id: number }>("/api/my/club/");
        // 2) грузим сводку
        const summary = await getJSON<ClubSummary>(`/api/clubs/${my.id}/summary/`);

        if (!cancelled) {
          setClub(summary);
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
      </Grid>
    </Box>
  );
}
