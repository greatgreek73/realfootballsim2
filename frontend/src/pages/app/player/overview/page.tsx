import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Breadcrumbs,
  Card,
  CardContent,
  Grid,
  Skeleton,
  Typography,
  Box,
  LinearProgress,
  Stack,
} from "@mui/material";
import { Link, useSearchParams } from "react-router-dom";

import PlayerProfileMenu from "./sections/player-profile-menu";

// Иконки карточек статов
import NiScreen from "@/icons/nexture/ni-screen";
import NiFloppyDisk from "@/icons/nexture/ni-floppy-disk";
import NiUsers from "@/icons/nexture/ni-users";
import NiHearts from "@/icons/nexture/ni-hearts";

// Радар (ваша версия требует radar.metrics)
import { RadarChart } from "@mui/x-charts"; // если не соберётся — поставьте @mui/x-charts и перезапустите dev

type Attr = { key: string; value: number };
type Attributes = Record<string, Attr[]>;

type ApiPlayer = {
  id: number;
  full_name: string;
  age: number;
  position: string;
  overall_rating: number;
  experience: number;
  player_class: number;
  club: { id: number; name: string } | null;
  attributes: Attributes;
};

function StatCard({
  icon,
  label,
  value,
  sub,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <Card component="div" className="flex flex-row items-center p-1">
      <Box className="bg-primary-light/10 flex h-24 w-16 flex-none items-center justify-center rounded-2xl">
        {icon}
      </Box>
      <CardContent>
        <Typography variant="body2" className="text-text-secondary leading-5">
          {label}
        </Typography>
        <Box className="flex flex-row items-center gap-2">
          <Typography variant="h5" className="text-leading-5">
            {value}
          </Typography>
          {sub && (
            <Typography variant="body2" className="text-text-secondary">
              {sub}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

function PrettyAttrName({ name }: { name: string }) {
  const label = name.replaceAll("_", " ");
  return <span style={{ textTransform: "capitalize" }}>{label}</span>;
}

export default function Page() {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id") ?? undefined;

  const [data, setData] = useState<ApiPlayer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;

    (async () => {
      try {
        setLoading(true);
        setError(null);

        // Пробуем /api/players/<id>/, если не сработает — /players/api/<id>/
        const endpoints = [`/api/players/${id}/`, `/players/api/${id}/`];
        let lastErr: any = null;

        for (const url of endpoints) {
          try {
            const res = await fetch(url, { cache: "no-store" });
            if (res.ok) {
              const json = (await res.json()) as ApiPlayer;
              if (!cancelled) setData(json);
              lastErr = null;
              break;
            } else {
              lastErr = new Error(`HTTP ${res.status} at ${url}`);
            }
          } catch (e) {
            lastErr = e;
          }
        }

        if (lastErr && !cancelled) throw lastErr;
      } catch (e: any) {
        if (!cancelled) setError(e.message ?? String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [id]);

  const title = data?.full_name ?? (id ? `Player #${id}` : "Player Overview");
  const attributes = data?.attributes ?? {};

  // Данные для радара
  const radar = useMemo(() => {
    const entries = Object.entries(attributes);
    const labels = entries.map(([group]) => group);
    const values = entries.map(([, attrs]) => {
      const sum = attrs.reduce((s, a) => s + (a.value ?? 0), 0);
      return Math.round(sum / Math.max(1, attrs.length));
    });
    return { labels, values };
  }, [attributes]);

  return (
    <Grid container spacing={5} className="w-full" size={12}>
      {/* Header */}
      <Grid container spacing={2.5} className="w-full" size={12}>
        <Grid size={{ md: "grow", xs: 12 }}>
          <Typography variant="h1" component="h1" className="mb-0">
            {title}
          </Typography>
          <Breadcrumbs>
            <Link to="/my-club">My Club</Link>
            <Link to="/my-club/players">Players</Link>
            <Typography variant="body2">{title}</Typography>
          </Breadcrumbs>
        </Grid>
      </Grid>

      {/* Alerts */}
      {!id && (
        <Grid size={12}>
          <Alert severity="info">
            Добавьте параметр <code>?id=&lt;ID&gt;</code> к URL (например, <code>/player/overview?id=8017</code>).
          </Alert>
        </Grid>
      )}
      {error && (
        <Grid size={12}>
          <Alert severity="error">Ошибка загрузки: {error}</Alert>
        </Grid>
      )}

      {/* ===== Основная сетка: левая колонка (меню) + правая колонка (контент) ===== */}
      <Grid container size={12}>
        {/* Левая колонка */}
        <Grid size={{ "3xl": 3, lg: 4, xs: 12 }}>
          <PlayerProfileMenu selected="overview" playerId={id} playerName={data?.full_name} />
        </Grid>

        {/* Правая колонка */}
        <Grid container size={{ "3xl": 9, lg: 8, xs: 12 }} spacing={2.5}>
          {/* 4 стат-карты */}
          <Grid container size={12} spacing={2.5}>
            {loading ? (
              <>
                <Grid size={{ lg: 3, xs: 12 }}>
                  <Skeleton variant="rounded" height={96} />
                </Grid>
                <Grid size={{ lg: 3, xs: 12 }}>
                  <Skeleton variant="rounded" height={96} />
                </Grid>
                <Grid size={{ lg: 3, xs: 12 }}>
                  <Skeleton variant="rounded" height={96} />
                </Grid>
                <Grid size={{ lg: 3, xs: 12 }}>
                  <Skeleton variant="rounded" height={96} />
                </Grid>
              </>
            ) : (
              <>
                <Grid size={{ lg: 3, xs: 12 }}>
                  <StatCard icon={<NiScreen className="text-primary" size={"large"} />} label="Overall Rating" value={data?.overall_rating ?? "-"} />
                </Grid>
                <Grid size={{ lg: 3, xs: 12 }}>
                  <StatCard icon={<NiFloppyDisk className="text-secondary" size={"large"} />} label="Experience" value={data?.experience ?? "-"} />
                </Grid>
                <Grid size={{ lg: 3, xs: 12 }}>
                  <StatCard icon={<NiUsers className="text-accent-1" size={"large"} />} label="Player Class" value={data?.player_class ?? "-"} />
                </Grid>
                <Grid size={{ lg: 3, xs: 12 }}>
                  <StatCard icon={<NiHearts className="text-accent-2" size={"large"} />} label="Age" value={data?.age ?? "-"} />
                </Grid>
              </>
            )}
          </Grid>

          {/* Attributes + Radar: 8/4 */}
          {!!data && (
            <Grid container size={12} spacing={2.5}>
              {/* Attributes */}
              <Grid size={{ "3xl": 8, lg: 8, xs: 12 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" component="h5" className="card-title">
                      Attributes
                    </Typography>

                    {Object.keys(attributes).length === 0 ? (
                      <Typography variant="body2" className="text-text-secondary">No attributes</Typography>
                    ) : (
                      <Stack spacing={2.5}>
                        {Object.entries(attributes).map(([groupName, attrs]) => (
                          <div key={groupName}>
                            <Typography variant="subtitle2" className="mb-1.5">{groupName}</Typography>
                            <Stack spacing={1.25}>
                              {attrs.map((a) => (
                                <div key={a.key} className="flex items-center gap-2">
                                  <div className="w-48">
                                    <Typography variant="body2"><PrettyAttrName name={a.key} /></Typography>
                                  </div>
                                  <LinearProgress
                                    variant="determinate"
                                    value={Math.max(0, Math.min(100, a.value))}
                                    sx={{ flex: 1, height: 8, borderRadius: 4 }}
                                  />
                                  <Typography variant="body2" className="w-10 text-right">{a.value}</Typography>
                                </div>
                              ))}
                            </Stack>
                          </div>
                        ))}
                      </Stack>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Radar */}
              <Grid size={{ "3xl": 4, lg: 4, xs: 12 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" component="h5" className="card-title">
                      Attribute Radar (avg by group)
                    </Typography>
                    {radar.labels.length === 0 ? (
                      <Typography variant="body2" className="text-text-secondary">No data</Typography>
                    ) : (
                      <RadarChart
                        height={360}
                        series={[{ data: radar.values, area: true }]}
                        radar={{
                          metrics: radar.labels,
                          max: 100,
                          labelGap: 22,
                        }}
                        axis={{
                          angle: { disableTicks: true, disableLine: true },
                          radius: { disableTicks: true, disableLine: true },
                        }}
                        grid={{ radial: { angle: 0 } }}
                      />
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Grid>
      </Grid>
    </Grid>
  );
}
