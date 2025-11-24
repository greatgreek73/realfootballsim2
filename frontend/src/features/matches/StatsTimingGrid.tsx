import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, Grid, List, ListItem, ListItemText, Typography } from "@mui/material";
import type { MatchDetail } from "@/api/matches";

type LineupEntry = {
  slot: string;
  slotLabel: string;
  playerName: string;
  position?: string;
  playerId?: number | null;
};

const normalizeLineup = (raw: unknown): LineupEntry[] => {
  if (!raw || typeof raw !== "object") return [];
  const source = (raw as any).lineup ?? raw;
  if (!source || typeof source !== "object") return [];

  return Object.entries(source).map(([slot, value]) => {
    const data = value as any;
    const slotLabel = data?.slotLabel || data?.label || `Slot ${slot}`;
    const playerId = data?.playerId ?? data?.player ?? data;
    const numericId = Number(playerId);
    const parsedId = Number.isFinite(numericId) ? numericId : null;
    const playerName =
      data?.playerName ||
      data?.name ||
      data?.player_name ||
      data?.full_name ||
      data?.displayName ||
      (parsedId !== null ? String(parsedId) : "No player");
    const position = data?.playerPosition || data?.position;
    return {
      slot: String(slot),
      slotLabel: String(slotLabel),
      playerName: String(playerName),
      position: position ? String(position) : undefined,
      playerId: parsedId,
    };
  });
};

export function StatsTimingGrid({ match }: { match: MatchDetail }) {
  const homeLineup = useMemo(() => normalizeLineup(match.home.lineup), [match.home.lineup]);
  const awayLineup = useMemo(() => normalizeLineup(match.away.lineup), [match.away.lineup]);

  type PlayerInfo = { id: number; name: string; position?: string };
  const [homePlayers, setHomePlayers] = useState<Record<number, PlayerInfo>>({});
  const [awayPlayers, setAwayPlayers] = useState<Record<number, PlayerInfo>>({});

  const shouldLookup = (entry: LineupEntry) =>
    entry.playerId &&
    (entry.playerName === String(entry.playerId) || entry.playerName === "No player" || !entry.position);

  useEffect(() => {
    const needsLookup = homeLineup.some(shouldLookup);
    if (!needsLookup || !match.home.id) return;
    fetch(`/clubs/detail/${match.home.id}/get-players/`, { credentials: "include" })
      .then((res) => res.json())
      .then((data: any[]) => {
        const map: Record<number, PlayerInfo> = {};
        (data || []).forEach((p: any) => {
          const id = Number(p?.id);
          if (!Number.isFinite(id)) return;
          const name = p?.name || `${p?.first_name ?? ""} ${p?.last_name ?? ""}`.trim() || String(id);
          map[id] = { id, name, position: p?.position ?? undefined };
        });
        setHomePlayers(map);
      })
      .catch(() => {
        /* ignore */
      });
  }, [homeLineup, match.home.id]);

  useEffect(() => {
    const needsLookup = awayLineup.some(shouldLookup);
    if (!needsLookup || !match.away.id) return;
    fetch(`/clubs/detail/${match.away.id}/get-players/`, { credentials: "include" })
      .then((res) => res.json())
      .then((data: any[]) => {
        const map: Record<number, PlayerInfo> = {};
        (data || []).forEach((p: any) => {
          const id = Number(p?.id);
          if (!Number.isFinite(id)) return;
          const name = p?.name || `${p?.first_name ?? ""} ${p?.last_name ?? ""}`.trim() || String(id);
          map[id] = { id, name, position: p?.position ?? undefined };
        });
        setAwayPlayers(map);
      })
      .catch(() => {
        /* ignore */
      });
  }, [awayLineup, match.away.id]);

  const resolveDisplay = (entry: LineupEntry, map: Record<number, PlayerInfo>) => {
    if (!entry.playerId) return entry;
    const found = map[entry.playerId];
    if (!found) return entry;
    return {
      ...entry,
      playerName: found.name || entry.playerName,
      position: found.position || entry.position,
    };
  };

  const displayHome = useMemo(
    () => homeLineup.map((entry) => resolveDisplay(entry, homePlayers)),
    [homeLineup, homePlayers]
  );
  const displayAway = useMemo(
    () => awayLineup.map((entry) => resolveDisplay(entry, awayPlayers)),
    [awayLineup, awayPlayers]
  );

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" className="mb-2">Home lineup</Typography>
            <Typography variant="body2" color="text.secondary" className="mb-2">
              {match.home.name} — tactic: {match.home.tactic ?? "-"}
            </Typography>
            {displayHome.length === 0 ? (
              <Typography variant="body2" color="text.secondary">Нет данных о составе.</Typography>
            ) : (
              <List dense>
                {displayHome.map((item) => (
                  <ListItem key={`${item.slot}-${item.playerName}`}>
                    <ListItemText
                      primary={item.position || item.slotLabel || `Slot ${item.slot}`}
                      secondary={item.playerName}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" className="mb-2">Away lineup</Typography>
            <Typography variant="body2" color="text.secondary" className="mb-2">
              {match.away.name} — tactic: {match.away.tactic ?? "-"}
            </Typography>
            {displayAway.length === 0 ? (
              <Typography variant="body2" color="text.secondary">Нет данных о составе.</Typography>
            ) : (
              <List dense>
                {displayAway.map((item) => (
                  <ListItem key={`${item.slot}-${item.playerName}`}>
                    <ListItemText
                      primary={item.position || item.slotLabel || `Slot ${item.slot}`}
                      secondary={item.playerName}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
