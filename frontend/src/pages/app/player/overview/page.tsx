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


  const hero = (
    <HeroBar
      title={title}
      tone="purple"
      kpis={[
        { label: "Overall", value: data?.overall_rating ?? "—" },
        { label: "Age", value: data?.age ?? "—" },
        { label: "Position", value: data?.position ?? "—" },
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
        Выберите параметр <code>?id=&lt;ID&gt;</code> в URL (например, <code>/player/overview?id=8017</code>).
      </Alert>
    );
  }
  if (error) {
    alerts.push(
      <Alert key="error" severity="error">Ошибка загрузки: {error}</Alert>
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
                        <Typography
                          key={row.id}
                          variant="subtitle2"
                          sx={{
                            textTransform: "uppercase",
                            fontSize: 11,
                            letterSpacing: 1,
                            px: 2,
                            py: 1,
                            bgcolor: "grey.100",
                          }}
                        >
                          {row.label}
                        </Typography>
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

        <DialogTitle>Дополнительная тренировка</DialogTitle>

        <DialogContent>

          {typeof data?.next_boost_cost === "number" && (

            <Typography variant="body2" className="mb-3 text-text-secondary">

              Стоимость тренировки: {data.next_boost_cost} токенов

            </Typography>

          )}

          <FormControl component="fieldset" fullWidth>

            <FormLabel component="legend">Выберите группу атрибутов</FormLabel>

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

            Отмена

          </Button>

          <Button

            onClick={handleTrainingConfirm}

            variant="contained"

            disabled={!selectedGroup || trainingLoading}

          >

            {trainingLoading ? "Выполняем..." : "Запустить"}

          </Button>

        </DialogActions>

      </Dialog>

    </>

  );

}

