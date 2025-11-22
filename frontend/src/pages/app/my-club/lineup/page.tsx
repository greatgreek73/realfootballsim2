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
  row: number;
  col: number;
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

// 4-4-2 formation layout on a 7-column grid (row top to bottom: GK, DEF, MID, ATT)
// Pitch grid (7 columns, 8 rows) inspired by reference layout; more slots than 11, but only GK + 10 outfield allowed.
const SLOT_DEFINITIONS: SlotDefinition[] = [
  // Forwards (row 1)
  { id: "f1", label: "LF", slotType: "forward", row: 1, col: 3 },
  { id: "f2", label: "CF", slotType: "forward", row: 1, col: 4 },
  { id: "f3", label: "RF", slotType: "forward", row: 1, col: 5 },
  // Attacking mids (row 2)
  { id: "am1", label: "LAM", slotType: "midfielder", row: 2, col: 2 },
  { id: "am2", label: "AM", slotType: "midfielder", row: 2, col: 4 },
  { id: "am3", label: "RAM", slotType: "midfielder", row: 2, col: 6 },
  // Central mids (row 3)
  { id: "cm1", label: "LCM", slotType: "midfielder", row: 3, col: 2 },
  { id: "cm2", label: "CM", slotType: "midfielder", row: 3, col: 3 },
  { id: "cm3", label: "CM", slotType: "midfielder", row: 3, col: 4 },
  { id: "cm4", label: "CM", slotType: "midfielder", row: 3, col: 5 },
  { id: "cm5", label: "RCM", slotType: "midfielder", row: 3, col: 6 },
  // Defensive mids (row 4)
  { id: "dm1", label: "LDM", slotType: "midfielder", row: 4, col: 2 },
  { id: "dm2", label: "DM", slotType: "midfielder", row: 4, col: 4 },
  { id: "dm3", label: "RDM", slotType: "midfielder", row: 4, col: 6 },
  // Defenders (row 5)
  { id: "d1", label: "LB", slotType: "defender", row: 5, col: 2 },
  { id: "d2", label: "LCB", slotType: "defender", row: 5, col: 3 },
  { id: "d3", label: "CB", slotType: "defender", row: 5, col: 4 },
  { id: "d4", label: "RCB", slotType: "defender", row: 5, col: 5 },
  { id: "d5", label: "RB", slotType: "defender", row: 5, col: 6 },
  // Goalkeeper (row 6)
  { id: "0", label: "GK", slotType: "goalkeeper", row: 6, col: 4 },
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
  const [limitWarning, setLimitWarning] = useState<string | null>(null);
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
  const hasGoalkeeper = Boolean(assignments["0"]);
  const fieldCount = useMemo(
    () => Object.entries(assignments).filter(([slotId]) => slotId !== "0").length,
    [assignments]
  );
  const totalSelected = fieldCount + (hasGoalkeeper ? 1 : 0);
  const isLineupValid = hasGoalkeeper && fieldCount <= 10;

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
        setLimitWarning(null);
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
      const nextFieldCount = Object.entries(next).filter(([id]) => id !== "0").length;
      if (nextFieldCount > 10) {
        setLimitWarning("You can assign only 10 outfield players (plus 1 goalkeeper).");
        return prev;
      }
      setLimitWarning(null);
      return next;
    });
    setSuccess(null);
  };

  const handleSave = useCallback(
    async (options?: { silent?: boolean }) => {
      if (!club?.id) return;
      if (!options?.silent) setSaving(true);
      if (options?.silent) setAutoSaving(true);
      if (!options?.silent) setError(null);
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
    if (!initialized || !club?.id || loading || !isLineupValid) return;
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
        { label: "Slots", value: `${Math.min(totalSelected, 11)}/11` },
        { label: "Tactic", value: tactic || "balanced" },
        { label: "GK required", value: hasGoalkeeper ? "Yes" : "Missing" },
        { label: "Players", value: players.length || "-" },
      ]}
      actions={
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button variant="outlined" onClick={handleReset} disabled={loading || saving}>
            Reset
          </Button>
          <Button variant="contained" onClick={() => handleSave()} disabled={loading || saving || !isLineupValid}>
            {saving ? "Saving..." : "Save lineup"}
          </Button>
        </Stack>
      }
    />
  );

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

        <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <Box
            sx={{
              borderRadius: 3,
              border: "1px solid",
              borderColor: "divider",
              p: { xs: 1.5, md: 2 },
              background: "linear-gradient(180deg, #f0fff4 0%, #ffffff 100%)",
              minHeight: 520,
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "center",
            }}
          >
            <Box sx={{ width: "100%", display: "flex", justifyContent: "center" }}>
              <Box
                sx={{
                  width: "100%",
                  maxWidth: 820,
                  display: "grid",
                  gridTemplateColumns: "repeat(7, minmax(0, 1fr))",
                  gridTemplateRows: "repeat(6, minmax(90px, 1fr))",
                  gap: { xs: 1.25, md: 1.75 },
                  alignItems: "start",
                  justifyItems: "center",
                  minHeight: 480,
                  transform: { xs: "scale(0.8)", md: "scale(0.75)" },
                  transformOrigin: "top center",
                  position: "relative",
                }}
              >
                {SLOT_DEFINITIONS.map((slot) => {
                  const assignment = assignments[slot.id];
                  const assignedPlayer = assignment ? players.find((p) => p.id === assignment.playerId) : undefined;
                  const draggingAllowed = dragging ? isSlotCompatible(dragging.slotType, slot.slotType) : false;
                  return (
                <Box
                  key={slot.id}
                  sx={{
                    gridColumn: slot.col,
                    gridRow: slot.row,
                    display: "flex",
                    alignItems: "stretch",
                  }}
                >
                    <Card
                      variant="outlined"
                      sx={{
                        flex: 1,
                        minWidth: 72,
                        maxWidth: 96,
                        borderStyle: draggingAllowed ? "dashed" : "solid",
                        borderColor: draggingAllowed ? "primary.main" : "divider",
                        transition: "border-color 0.2s ease, background-color 0.2s ease",
                        backgroundColor: draggingAllowed ? "primary.main/12" : "background.paper",
                        minHeight: 0,
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
                    >
                      <CardContent sx={{ p: 0.4 }}>
                        <Stack spacing={0.2} alignItems="center">
                          <Typography
                            variant="body2"
                            fontWeight={700}
                            textAlign="center"
                            sx={{ lineHeight: 1, fontSize: 11 }}
                          >
                            {slot.label}
                          </Typography>
                          <Box
                            sx={{
                              borderRadius: 1,
                              border: "1px dashed",
                              borderColor: draggingAllowed ? "primary.main" : "divider",
                              minHeight: 24,
                              width: "100%",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              backgroundColor: "grey.50",
                              px: 0.4,
                              py: 0.2,
                            }}
                          >
                            {assignedPlayer ? (
                              <Stack
                                spacing={0.15}
                                sx={{ width: "100%", cursor: "grab" }}
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
                                <Typography variant="caption" fontWeight={600} noWrap sx={{ lineHeight: 1.1 }}>
                                  {assignedPlayer.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" noWrap sx={{ lineHeight: 1.1 }}>
                                  {assignedPlayer.position}
                                </Typography>
                              </Stack>
                            ) : (
                              <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.1 }}>
                                Drag player
                              </Typography>
                            )}
                          </Box>
                        </Stack>
                      </CardContent>
                    </Card>
                  </Box>
                  );
                })}
              </Box>
            </Box>
          </Box>
        </Box>
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
      {limitWarning && <Alert severity="warning">{limitWarning}</Alert>}
      {!error && !success && (
        <Typography variant="body2" color="text.secondary">
          Drag players onto slots. Changes auto-save when a goalkeeper is set; you still must set exactly one goalkeeper.
        </Typography>
      )}
    </Stack>
  );

  return (
    <PageShell
      hero={hero}
      top={top}
      main={
        loading ? (
          <Stack alignItems="center" justifyContent="center" sx={{ minHeight: 320 }}>
            <CircularProgress />
          </Stack>
        ) : (
          mainContent
        )
      }
      aside={loading ? undefined : asideContent}
      bottomSplit="67-33"
    />
  );
}
