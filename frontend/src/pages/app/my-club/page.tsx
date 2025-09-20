import { useEffect, useState } from "react";

import { Alert, Box, Grid, Typography } from "@mui/material";

import {
  ClubActions,
  ClubActivity,
  ClubBanner,
  ClubFinancePlaceholder,
  ClubSchedule,
  ClubStats,
} from "./sections";

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
  return (await res.json()) as T;
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

        const my = await getJSON<{ id: number }>("/api/my/club/");
        const summary = await getJSON<ClubSummary>(`/api/clubs/${my.id}/summary/`);

        if (!cancelled) {
          setClub(summary);
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load club data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  // TODO: Wire upcoming fixtures, activity feed, and finance trends once the corresponding APIs are available.
  return (
    <Box className="p-2 sm:p-4">
      {error && (
        <Alert severity="error" className="mb-3">
          {error}
        </Alert>
      )}

      <Grid container spacing={5}>
        <Grid container spacing={2.5} className="w-full" size={12}>
          <Grid size={{ xs: 12, md: "grow" }}>
            <Typography variant="h1" component="h1" className="mb-0">
              {club?.name ?? "My Club"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {club ? [club.country, club.league].filter(Boolean).join(" - ") : "Welcome back!"}
            </Typography>
          </Grid>
        </Grid>

        <Grid container size={12} spacing={2.5}>
          <Grid size={{ lg: 8, xs: 12 }}>
            <ClubBanner club={club} loading={loading} />
          </Grid>
          <Grid size={{ lg: 4, xs: 12 }}>
            <ClubActions club={club} loading={loading} />
          </Grid>
        </Grid>

        <Grid container size={12} spacing={2.5}>
          <Grid size={{ lg: 8, xs: 12 }}>
            <Grid container size={12} spacing={2.5}>
              <ClubStats club={club} loading={loading} />
            </Grid>
          </Grid>
          <Grid size={{ lg: 4, xs: 12 }}>
            <ClubActivity loading={loading} />
          </Grid>
        </Grid>

        <Grid container size={12} spacing={2.5}>
          <Grid size={{ lg: 6, xs: 12 }}>
            <ClubSchedule loading={loading} />
          </Grid>
          <Grid size={{ lg: 6, xs: 12 }}>
            <ClubFinancePlaceholder loading={loading} />
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}
