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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Stack,
} from "@mui/material";

import { Link, useSearchParams } from "react-router-dom";

import { alpha } from "@mui/material/styles";

import { getCsrfToken } from "@/lib/apiClient";
import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";



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

  avatar_url?: string | null;

  boost_count?: number;

  next_boost_cost?: number;

  is_goalkeeper?: boolean;

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
  const [trainingDialogOpen, setTrainingDialogOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [trainingLoading, setTrainingLoading] = useState(false);
  const [trainingAlert, setTrainingAlert] = useState<{ severity: "success" | "error"; message: string } | null>(null);
  const [lastTrainingChanges, setLastTrainingChanges] = useState<Record<string, number>>({});


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

              if (!cancelled) {
                setData(json);
                setLastTrainingChanges({});
              }
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

  const attributeGroups = useMemo(() => Object.keys(attributes), [attributes]);


  useEffect(() => {

    if (!attributeGroups.length) {

      setSelectedGroup(null);

      return;

    }

    setSelectedGroup((prev) =>

      prev && attributeGroups.includes(prev) ? prev : attributeGroups[0]

    );

  }, [attributeGroups]);



  const formatGroupName = (name: string) => name.replaceAll("_", " ");



  const getAttributeColor = (value: number) => {

    if (value >= 81) return "#101212";

    if (value >= 51) return "#4C63B6";

    if (value >= 26) return "#C27C2C";

    return "#B3473C";

  };



  type AttributeRow =

    | { type: "group"; id: string; label: string }
    | {
        type: "attr";
        id: string;
        label: string;
        value: number;
        zebra: boolean;
        color: string;
        change?: number;
      };

  const {
    rows: attributeRows,
    sum: attributeSum,
    count: attributeCount,
  } = useMemo(() => {
    const entries = Object.entries(attributes ?? {}) as [string, Attr[]][];
    let zebraToggle = false;
    const rows: AttributeRow[] = [];
    let sum = 0;
    let count = 0;


    entries.forEach(([groupName, attrList]) => {

      const safeList = Array.isArray(attrList) ? attrList : [];

      if (safeList.length === 0) return;



      rows.push({ type: "group", id: `group-${groupName}`, label: groupName });



      safeList.forEach((attr) => {

        zebraToggle = !zebraToggle;

        const numericValue = Number(attr.value ?? 0);

        const safeValue = Number.isFinite(numericValue) ? Math.round(numericValue) : 0;

        const clampedValue = Math.max(0, Math.min(100, safeValue));



        const changeRaw = lastTrainingChanges?.[attr.key] ?? 0;
        const changeValue = Number.isFinite(changeRaw) ? Number(changeRaw) : 0;

        rows.push({
          type: "attr",
          id: `${groupName}-${attr.key}`,
          label: attr.key,
          value: safeValue,
          zebra: zebraToggle,
          color: getAttributeColor(clampedValue),
          change: changeValue !== 0 ? changeValue : undefined,
        });

        sum += safeValue;
        count += 1;
      });
    });



    return { rows, sum, count };
  }, [attributes, lastTrainingChanges]);


  // Плейсхолдер для аватара (если нет avatar_url с бэка)

  const avatarUrl = data?.avatar_url ?? "/img/avatar-2.jpg"; // ← добавлено



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



  const handleTrainingOpen = () => {

    if (!attributeGroups.length) {

      setTrainingAlert({

        severity: "error",

        message: "No attribute groups available for training.",

      });

      return;

    }

    setTrainingAlert(null);

    setTrainingDialogOpen(true);

  };



  const handleTrainingDialogClose = () => {

    if (trainingLoading) return;

    setTrainingDialogOpen(false);

  };



  const handleTrainingConfirm = async () => {

    if (!id || !selectedGroup) return;

    try {

      setTrainingLoading(true);

      const csrfToken = await getCsrfToken();

      const res = await fetch(`/api/players/${id}/extra-training/`, {

        method: "POST",

        headers: {

          "Content-Type": "application/json",

          "X-CSRFToken": csrfToken,

        },

        credentials: "include",

        body: JSON.stringify({ group: selectedGroup }),

      });



      let json: any = null;

      try {

        json = await res.json();

      } catch {

        // ignore JSON parse errors, обработаем ниже

      }



      if (!res.ok || !json?.success) {

        const message =

          json?.message ?? `Could not apply training (${res.status} ${res.statusText}).`;

        setTrainingAlert({ severity: "error", message });

        return;

      }



      setData(json.player as ApiPlayer);
      setLastTrainingChanges((json.changes ?? {}) as Record<string, number>);
      setTrainingAlert({
        severity: "success",
        message: `Training applied for ${formatGroupName(json.group ?? selectedGroup)}. Tokens left: ${json.tokens_left ?? "?"}.`,
      });
      setTrainingDialogOpen(false);

    } catch (err: any) {

      setTrainingAlert({

        severity: "error",

        message: err?.message ?? "Could not apply training.",

      });

    } finally {

      setTrainingLoading(false);

    }

  };



  const hero = (
    <HeroBar
      title={title}
      subtitle="Detailed breakdown of player attributes and training"
      tone="purple"
      kpis={[

        { label: "Overall", value: data?.overall_rating ?? "-" },

        { label: "Age", value: data?.age ?? "-" },

        { label: "Position", value: data?.position ?? "-" },

        { label: "Club", value: data?.club?.name ?? "Free Agent" },

      ]}

      actions={

        <Button component={Link} to="/my-club/players" size="small" variant="outlined">

          All players

        </Button>

      }

    />

  );



  const alerts: React.ReactNode[] = [];

  if (!id) {

    alerts.push(

      <Alert key="missing-id" severity="info">

        Provide player id via <code>?id=&lt;ID&gt;</code> in URL (e.g. <code>/player/overview?id=8017</code>.)

      </Alert>

    );

  }

  if (error) {

    alerts.push(

      <Alert key="error" severity="error">Error: {error}</Alert>

    );

  }

  if (trainingAlert) {

    alerts.push(

      <Alert key="training" severity={trainingAlert.severity} onClose={() => setTrainingAlert(null)}>

        {trainingAlert.message}

      </Alert>

    );

  }

  const alertsSection = alerts.length ? <Stack spacing={2}>{alerts}</Stack> : undefined;



  const statCardsSection = (

    <Grid container spacing={2.5}>

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

            <StatCard

              icon={<NiScreen className="text-primary" size={"large"} />}

              label="Overall Rating"

              value={attributeCount > 0 ? attributeSum : "-"}

            />

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

  );



  const attributesSection =

    !!data && (

      <Grid container spacing={2.5}>

        <Grid size={{ "3xl": 8, lg: 8, xs: 12 }}>

          <Card>

            <CardContent>

              <Typography variant="h5" component="h5" className="card-title">

                Attributes

              </Typography>



              {Object.keys(attributes).length === 0 ? (

                <Typography variant="body2" className="text-text-secondary">No attributes</Typography>

              ) : (

                <Box

                  sx={(theme) => ({

                    mt: 2,

                    borderRadius: 3,

                    border: "1px solid",

                    borderColor: theme.palette.divider,

                    overflow: "hidden",

                  })}

                >

                  {attributeRows.map((row) => {

                    if (row.type === "group") {

                      return (

                        <Box

                          key={row.id}

                          sx={(theme) => ({

                            px: 2,

                            py: 1.25,

                            backgroundColor: alpha(theme.palette.primary.main, theme.palette.mode === "dark" ? 0.24 : 0.08),

                            color: theme.palette.primary.main,

                            textTransform: "capitalize",

                            fontWeight: 600,

                            fontSize: theme.typography.pxToRem(13),

                          })}

                        >

                          {row.label}

                        </Box>

                      );

                    }



                    return (

                      <Box

                        key={row.id}

                        sx={(theme) => ({

                          display: "flex",

                          alignItems: "center",

                          justifyContent: "space-between",

                          gap: 1.25,

                          px: 2,

                          py: 1.1,

                          borderTop: "1px solid",

                          borderColor: theme.palette.divider,

                          backgroundColor: row.zebra

                            ? alpha(row.color, theme.palette.mode === "dark" ? 0.24 : 0.08)

                            : "transparent",

                          transition: "background-color 0.15s ease-in-out",

                        })}

                      >

                        <Typography

                          variant="body2"

                          sx={{

                            textTransform: "capitalize",

                            color: "text.secondary",

                            flex: 1,

                          }}

                        >

                          <PrettyAttrName name={row.label} />

                        </Typography>

                        <Box

                          sx={{

                            minWidth: 36,

                            textAlign: "right",

                            fontWeight: 700,

                            color:

                              row.change && row.change > 0

                                ? "success.main"

                                : row.change && row.change < 0

                                ? "error.main"

                                : "inherit",

                          }}

                        >

                          {typeof row.change === "number" && row.change !== 0

                            ? row.change > 0

                              ? `+${row.change}`

                              : row.change

                            : ""}

                        </Box>

                        <Box

                          component="span"

                          sx={(theme) => ({

                            display: "inline-flex",

                            alignItems: "center",

                            justifyContent: "center",

                            minWidth: 36,

                            px: 1.25,

                            py: 0.25,

                            borderRadius: 999,

                            fontWeight: 600,

                            fontVariantNumeric: "tabular-nums",

                            backgroundColor: alpha(row.color, theme.palette.mode === "dark" ? 0.32 : 0.14),

                            color: row.color,

                          })}

                        >

                          {row.value}

                        </Box>

                      </Box>

                    );

                  })}

                </Box>

              )}

            </CardContent>

          </Card>

        </Grid>



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

    );



  const asideContent = (

    <PlayerProfileMenu

      selected="overview"

      playerId={id}

      playerName={data?.full_name}

      avatarUrl={avatarUrl}

      onTraining={handleTrainingOpen}

      trainingDisabled={loading || !attributeGroups.length}

      trainingLoading={trainingLoading}

    />

  );



  const mainContent = (

    <Stack spacing={3}>

      {statCardsSection}

      {attributesSection}

    </Stack>

  );



  const breadcrumbs = (

    <Breadcrumbs>

      <Link to="/my-club">My Club</Link>

      <Link to="/my-club/players">Players</Link>

      <Typography variant="body2">{title}</Typography>

    </Breadcrumbs>

  );



  return (



    <>



      <PageShell

        hero={hero}

        header={breadcrumbs}

        top={alertsSection}

        main={mainContent}

        aside={asideContent}

        bottomSplit="67-33"

      />



      <Dialog



        open={trainingDialogOpen}



        onClose={handleTrainingDialogClose}



        fullWidth



        maxWidth="xs"



      >



        <DialogTitle>Assign training</DialogTitle>



        <DialogContent>



          {typeof data?.next_boost_cost === "number" && (



            <Typography variant="body2" className="mb-3 text-text-secondary">



              Training cost: {data.next_boost_cost} tokens



            </Typography>



          )}



          <FormControl component="fieldset" fullWidth>



            <FormLabel component="legend">Choose attribute group</FormLabel>



            <RadioGroup



              value={selectedGroup ?? ""}



              onChange={(event) => setSelectedGroup(event.target.value)}



            >



              {attributeGroups.map((group) => (



                <FormControlLabel



                  key={group}



                  value={group}



                  control={<Radio />}



                  label={formatGroupName(group)}



                />



              ))}



            </RadioGroup>



          </FormControl>



        </DialogContent>



        <DialogActions>



          <Button onClick={handleTrainingDialogClose} disabled={trainingLoading}>



            Cancel



          </Button>



          <Button



            onClick={handleTrainingConfirm}



            variant="contained"



            disabled={!selectedGroup || trainingLoading}



          >



            {trainingLoading ? "Applying..." : "Apply"}



          </Button>



        </DialogActions>



      </Dialog>



    </>



  );



}