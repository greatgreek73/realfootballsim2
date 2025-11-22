import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import HeroBar from "@/components/ui/HeroBar";
import PageShell from "@/components/ui/PageShell";
import { getCsrfToken } from "@/lib/apiClient";

type SlotType = "goalkeeper" | "defender" | "midfielder" | "forward";

type SlotDefinition = {
  id: string;
  label: string;
  slotType: SlotType;
};

type PlayerOption = {
  id: number;
  name: string;
  position: string;
  playerClass: number;
  attributes?: { attack?: number; defense?: number };
  avatar_url?: string | null;
};

type LineupPayload = Record<
  string,
  {
    playerId: number;
    playerPosition: string;
    slotType: SlotType;
    slotLabel: string;
  }
>;

type LineupResponse = {
  lineup: LineupPayload;
  tactic: string;
};

type ClubSummary = { id: number; name: string };

const normalizeLineup = (value: any): LineupPayload => {
  if (!value || typeof value !== "object") return {};
  const result: LineupPayload = {};
  Object.entries(value).forEach(([slotId, data]) => {
    if (!data || typeof data !== "object") return;
    const playerId = Number((data as any).playerId);
    if (!Number.isFinite(playerId)) return;
    const slotMeta = SLOT_DEFINITIONS.find((s) => s.id === slotId);
    result[slotId] = {
      playerId,
      playerPosition: String((data as any).playerPosition || ""),
      slotType: ((data as any).slotType as SlotType) || slotMeta?.slotType || "midfielder",
      slotLabel: String((data as any).slotLabel || slotMeta?.label || slotId),
    };
  });
  return result;
};

const SLOT_DEFINITIONS: SlotDefinition[] = [
  { id: "0", label: "GK", slotType: "goalkeeper" },
  { id: "1", label: "LB", slotType: "defender" },
  { id: "2", label: "CB", slotType: "defender" },
  { id: "3", label: "CB", slotType: "defender" },
  { id: "4", label: "RB", slotType: "defender" },
  { id: "5", label: "LM", slotType: "midfielder" },
  { id: "6", label: "CM", slotType: "midfielder" },
  { id: "7", label: "RM", slotType: "midfielder" },
  { id: "8", label: "LF", slotType: "forward" },
  { id: "9", label: "ST", slotType: "forward" },
  { id: "10", label: "RF", slotType: "forward" },
];

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text.slice(0, 200)}`);
  }
  return (await res.json()) as T;
}

const positionToSlotType = (position?: string): SlotType | null => {
  if (!position) return null;
  const p = position.toLowerCase();
  if (p.includes("keeper") || p.includes("goalkeeper") || p === "gk") return "goalkeeper";
  if (p.includes("back") || p.includes("defender") || p.includes("centre-back") || p.includes("cb")) {
    return "defender";
  }
  if (p.includes("mid")) return "midfielder";
  if (p.includes("wing") || p.includes("striker") || p.includes("forward") || p.includes("attacker")) {
    return "forward";
  }
  return null;
};

export default function LineupPage() {
  const [club, setClub] = useState<ClubSummary | null>(null);
  const [players, setPlayers] = useState<PlayerOption[]>([]);
  const [assignments, setAssignments] = useState<LineupPayload>({});
  const [tactic, setTactic] = useState("balanced");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [autoSaving, setAutoSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [dragging, setDragging] = useState<{ playerId: number; slotType: SlotType | null } | null>(null);
  const [initialized, setInitialized] = useState(false);
  const autoSaveTimer = useRef<number | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError(null);

        const me = await fetchJSON<{ id: number }>("/api/my/club/");
        const clubSummary = await fetchJSON<ClubSummary>(`/api/clubs/${me.id}/summary/`);
        const [playersData, lineupData] = await Promise.all([
          fetchJSON<PlayerOption[]>(`/clubs/detail/${me.id}/get-players/`),
          fetchJSON<Partial<LineupResponse>>(`/clubs/detail/${me.id}/get-team-lineup/`),
        ]);

        setClub({ id: clubSummary.id, name: clubSummary.name });
        setPlayers(playersData ?? []);
        setTactic(lineupData?.tactic || "balanced");
        setAssignments(normalizeLineup(lineupData?.lineup));
        setInitialized(true);
      } catch (e: any) {
        setError(e?.message || "Failed to load lineup data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const assignedPlayerIds = useMemo(() => new Set(Object.values(assignments).map((a) => a.playerId)), [assignments]);

  const isSlotCompatible = (playerType: SlotType | null, slotType: SlotType) => {
    if (!playerType) return true;
    return playerType === slotType;
  };

  const getEligiblePlayers = (slot: SlotDefinition): PlayerOption[] => {
    const current = assignments[slot.id]?.playerId;
    const eligibleType = slot.slotType;
    return players.filter((p) => {
      const mapped = positionToSlotType(p.position);
      const allowed = isSlotCompatible(mapped, eligibleType);
      const available = !assignedPlayerIds.has(p.id) || p.id === current;
      return allowed && available;
    });
  };

  const handleAssign = (slot: SlotDefinition, playerId: number | "") => {
    setAssignments((prev) => {
      const next = { ...prev };
      if (playerId !== "") {
        Object.entries(next).forEach(([slotId, data]) => {
          if (slotId !== slot.id && data.playerId === playerId) {
            delete next[slotId];
          }
        });
      }
      if (playerId === "") {
        delete next[slot.id];
        return next;
      }
      const player = players.find((p) => p.id === playerId);
      if (!player) return prev;
      next[slot.id] = {
        playerId,
        playerPosition: player.position,
        slotType: slot.slotType,
        slotLabel: slot.label,
      };
      return next;
    });
    setSuccess(null);
  };

  const handleSave = useCallback(
    async (options?: { silent?: boolean }) => {
      if (!club?.id) return;
      if (!options?.silent) setSaving(true);
      if (options?.silent) setAutoSaving(true);
      setError(null);
      if (!options?.silent) setSuccess(null);
      try {
        const payload = {
          lineup: assignments,
          tactic,
        };
        const csrftoken = await getCsrfToken();
        const res = await fetch(`/clubs/detail/${club.id}/save-team-lineup/`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
          },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
          throw new Error(data.error || "Failed to save lineup");
        }
        if (!options?.silent) setSuccess("Lineup saved");
      } catch (e: any) {
        setError(e?.message || "Failed to save lineup");
      } finally {
        if (!options?.silent) setSaving(false);
        setAutoSaving(false);
      }
    },
    [club?.id, assignments, tactic]
  );

  const handleReset = () => {
    setAssignments({});
    setSuccess(null);
  };

  useEffect(() => {
    if (!initialized || !club?.id || loading) return;
    if (autoSaveTimer.current) {
      clearTimeout(autoSaveTimer.current);
    }
    autoSaveTimer.current = window.setTimeout(() => {
      handleSave({ silent: true }).catch((e) => setError(e?.message || "Failed to save lineup"));
    }, 500);
    return () => {
      if (autoSaveTimer.current) {
        clearTimeout(autoSaveTimer.current);
      }
    };
  }, [assignments, tactic, club?.id, loading, initialized, handleSave]);

  const handleDragStart = (player: PlayerOption) => {
    setDragging({ playerId: player.id, slotType: positionToSlotType(player.position) });
  };

  const handleDragEnd = () => setDragging(null);

  const handleDropToSlot = (slot: SlotDefinition, playerId: number) => {
    const player = players.find((p) => p.id === playerId);
    if (!player) return;
    const mapped = positionToSlotType(player.position);
    if (!isSlotCompatible(mapped, slot.slotType)) return;
    handleAssign(slot, playerId);
  };

  const handleDropToBench = (playerId: number) => {
    setAssignments((prev) => {
      const next = { ...prev };
      Object.entries(next).forEach(([slotId, data]) => {
        if (data.playerId === playerId) delete next[slotId];
      });
      return next;
    });
    setSuccess(null);
  };

  const renderPlayerBadge = (p: PlayerOption, assigned?: boolean) => (
    <Stack
      key={p.id}
      direction="row"
      spacing={1}
      alignItems="center"
      justifyContent="space-between"
      sx={{
        border: "1px solid",
        borderColor: assigned ? "divider" : "grey.200",
        borderRadius: 2,
        px: 1.5,
        py: 1,
        opacity: assigned ? 0.6 : 1,
        backgroundColor: "background.paper",
      }}
      draggable
      onDragStart={(e) => {
        handleDragStart(p);
        e.dataTransfer.setData("application/json", JSON.stringify({ playerId: p.id, from: "bench" }));
      }}
      onDragEnd={handleDragEnd}
    >
      <Box>
        <Typography variant="body2" fontWeight={600}>
          {p.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {p.position}
        </Typography>
      </Box>
      <Stack direction="row" spacing={1} alignItems="center">
        <Chip size="small" label={`ATT ${p.attributes?.attack ?? "-"}`} variant="outlined" />
        <Chip size="small" label={`DEF ${p.attributes?.defense ?? "-"}`} variant="outlined" />
        {assigned && <Chip size="small" color="info" label="In lineup" />}
      </Stack>
    </Stack>
  );

  const hero = (
    <HeroBar
      title="Lineup"
      subtitle={club ? `Set your starting XI for ${club.name}` : "Set your starting XI"}
      tone="green"
      kpis={[
        { label: "Slots", value: `${Object.keys(assignments).length}/11` },
        { label: "Tactic", value: tactic || "balanced" },
        { label: "GK required", value: assignments["0"] ? "Yes" : "Missing" },
        { label: "Players", value: players.length || "-" },
      ]}
      actions={
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button variant="outlined" onClick={handleReset} disabled={loading || saving}>
            Reset
          </Button>
          <Button variant="contained" onClick={handleSave} disabled={loading || saving}>
            {saving ? "Saving..." : "Save lineup"}
          </Button>
        </Stack>
      }
    />
  );

  if (loading) {
    return (
      <PageShell
        hero={hero}
        main={
          <Stack alignItems="center" justifyContent="center" sx={{ minHeight: 320 }}>
            <CircularProgress />
          </Stack>
        }
      />
    );
  }

  const mainContent = (
    <Card sx={{ height: "100%" }}>
      <CardContent sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ xs: "flex-start", sm: "center" }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel id="tactic-select-label">Tactic</InputLabel>
            <Select
              labelId="tactic-select-label"
              value={tactic}
              label="Tactic"
              onChange={(e) => setTactic(String(e.target.value))}
            >
              <MenuItem value="balanced">Balanced</MenuItem>
              <MenuItem value="defensive">Defensive</MenuItem>
              <MenuItem value="attacking">Attacking</MenuItem>
              <MenuItem value="counter">Counter</MenuItem>
            </Select>
          </FormControl>
          <Chip
            color={assignments["0"] ? "success" : "warning"}
            label={assignments["0"] ? "Goalkeeper set" : "Goalkeeper missing"}
          />
        </Stack>

        <Grid container spacing={2}>
          {SLOT_DEFINITIONS.map((slot) => {
            const assignment = assignments[slot.id];
            const assignedPlayer = assignment ? players.find((p) => p.id === assignment.playerId) : undefined;
            const draggingAllowed = dragging ? isSlotCompatible(dragging.slotType, slot.slotType) : false;
            const eligible = getEligiblePlayers(slot);
            return (
              <Grid item xs={12} sm={6} md={4} key={slot.id}>
                <Card
                  variant="outlined"
                  sx={{
                    borderStyle: draggingAllowed ? "dashed" : "solid",
                    borderColor: draggingAllowed ? "primary.main" : "divider",
                    transition: "border-color 0.2s ease, background-color 0.2s ease",
                    backgroundColor: draggingAllowed ? "primary.main/8" : "background.paper",
                  }}
                  onDragOver={(e) => {
                    if (!draggingAllowed) return;
                    e.preventDefault();
                  }}
                  onDrop={(e) => {
                    e.preventDefault();
                    try {
                      const raw = e.dataTransfer.getData("application/json");
                      const parsed = raw ? JSON.parse(raw) : null;
                      const playerId = parsed?.playerId ? Number(parsed.playerId) : NaN;
                      if (Number.isFinite(playerId)) {
                        handleDropToSlot(slot, playerId);
                      }
                    } catch {
                      /* ignore */
                    } finally {
                      handleDragEnd();
                    }
                  }}
                  onDragLeave={() => {
                    /* noop, style handled by state */
                  }}
                >
                  <CardContent>
                    <Stack spacing={1.25}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography variant="subtitle1">{slot.label}</Typography>
                        <Chip size="small" label={slot.slotType} color="default" />
                      </Stack>
                      <FormControl fullWidth size="small">
                        <InputLabel id={`slot-${slot.id}-label`}>Select player</InputLabel>
                        <Select
                          labelId={`slot-${slot.id}-label`}
                          label="Select player"
                          value={assignment?.playerId ?? ""}
                          onChange={(e) => handleAssign(slot, e.target.value as number | "")}
                        >
                          <MenuItem value="">
                            <em>Empty</em>
                          </MenuItem>
                          {eligible.map((p) => (
                            <MenuItem key={p.id} value={p.id}>
                              <Stack direction="row" spacing={1} alignItems="center">
                                <span>{p.name}</span>
                                <Chip size="small" label={p.position} />
                                <Chip size="small" variant="outlined" label={`ATT ${p.attributes?.attack ?? "-"}`} />
                                <Chip size="small" variant="outlined" label={`DEF ${p.attributes?.defense ?? "-"}`} />
                              </Stack>
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                      {assignedPlayer && (
                        <Box
                          sx={{
                            borderRadius: 2,
                            border: "1px solid",
                            borderColor: "divider",
                            px: 1.25,
                            py: 0.75,
                            backgroundColor: "grey.50",
                            cursor: "grab",
                          }}
                          draggable
                          onDragStart={(e) => {
                            handleDragStart(assignedPlayer);
                            e.dataTransfer.setData(
                              "application/json",
                              JSON.stringify({ playerId: assignedPlayer.id, from: "slot", slotId: slot.id })
                            );
                          }}
                          onDragEnd={handleDragEnd}
                        >
                          <Typography variant="body2" fontWeight={600}>
                            {assignedPlayer.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {assignedPlayer.position}
                          </Typography>
                        </Box>
                      )}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </CardContent>
    </Card>
  );

  const asideContent = (
    <Card sx={{ height: "100%" }}>
      <CardContent sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Typography variant="h6">Available players</Typography>
        <Divider />
        <Stack
          spacing={1.5}
          sx={{ maxHeight: 520, overflowY: "auto" }}
          onDragOver={(e) => {
            const raw = e.dataTransfer.getData("application/json");
            if (raw) e.preventDefault();
          }}
          onDrop={(e) => {
            e.preventDefault();
            try {
              const raw = e.dataTransfer.getData("application/json");
              const parsed = raw ? JSON.parse(raw) : null;
              const playerId = parsed?.playerId ? Number(parsed.playerId) : NaN;
              if (Number.isFinite(playerId)) {
                handleDropToBench(playerId);
              }
            } catch {
              /* ignore */
            } finally {
              handleDragEnd();
            }
          }}
        >
          {players.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              No players found.
            </Typography>
          )}
          {players.map((p) => renderPlayerBadge(p, assignedPlayerIds.has(p.id)))}
        </Stack>
      </CardContent>
    </Card>
  );

  const top = (
    <Stack spacing={1}>
      {error && <Alert severity="error">{error}</Alert>}
      {success && <Alert severity="success">{success}</Alert>}
      {!error && !success && (
        <Typography variant="body2" color="text.secondary">
          Drag players onto slots (or use selectors). Changes auto-save; you still must set exactly one goalkeeper.
        </Typography>
      )}
    </Stack>
  );

  return <PageShell hero={hero} top={top} main={mainContent} aside={asideContent} bottomSplit="67-33" />;
}
