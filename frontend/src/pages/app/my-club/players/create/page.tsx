import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Breadcrumbs,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import SportsSoccerIcon from "@mui/icons-material/SportsSoccer";
import MilitaryTechIcon from "@mui/icons-material/MilitaryTech";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import QueryBuilderIcon from "@mui/icons-material/QueryBuilder";
import PersonAddAltIcon from "@mui/icons-material/PersonAddAlt";
import { Link, useNavigate } from "react-router-dom";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { getJSON } from "@/lib/apiClient";

/** Тип ответа списка игроков в вашем API */
type ApiPlayer = {
  id: number;
  name: string;
  position: string;
  cls: number | string;
};
type PlayersList = { count: number; results: ApiPlayer[] };

/** Справочник позиций */
const POSITIONS = [
  "Goalkeeper",
  "Right Back",
  "Center Back",
  "Left Back",
  "Right Midfielder",
  "Central Midfielder",
  "Left Midfielder",
  "Center Forward",
];

/** Читаем CSRF cookie (для POST /api/players/<id>/generate-avatar/) */
function getCsrfToken(): string | undefined {
  const m = document.cookie.match(/(^|;\\s*)csrftoken=([^;]+)/);
  return m ? decodeURIComponent(m[2]) : undefined;
}

/** Надёжный считыватель списка игроков без кэша */
async function fetchPlayersRaw(clubId: number): Promise<ApiPlayer[]> {
  const url = `/api/clubs/${clubId}/players/?_=${Date.now()}`;
  const res = await fetch(url, { credentials: "include", cache: "no-store" });
  if (!res.ok) throw new Error(`Players fetch failed: ${res.status}`);
  const data = await res.json();
  if (Array.isArray(data)) return data as ApiPlayer[];
  if (data && Array.isArray(data.results)) return data.results as ApiPlayer[];
  throw new Error("Unexpected players payload");
}

/** Поиск нового ID по разнице списков c тайм-аутом и прогрессом */
async function pollForNewPlayer(
  clubId: number,
  beforeIds: number[],
  onTick?: (attempt: number, max: number) => void
): Promise<number | null> {
  const ATTEMPTS = 20;
  const DELAY_MS = 800;

  for (let i = 1; i <= ATTEMPTS; i++) {
    onTick?.(i, ATTEMPTS);
    await new Promise((r) => setTimeout(r, DELAY_MS));

    try {
      const after = await fetchPlayersRaw(clubId);
      const afterIds = after.map((p) => p.id);
      const diff = afterIds.filter((id) => !beforeIds.includes(id));
      if (diff.length) {
        diff.sort((a, b) => b - a);
        return diff[0];
      }
    } catch {
      // продолжаем попытки
    }
  }
  return null;
}

export default function CreatePlayerPage() {
  const navigate = useNavigate();

  const [clubId, setClubId] = useState<number | null>(null);
  const [beforeIds, setBeforeIds] = useState<number[]>([]);

  const [position, setPosition] = useState<string>("Center Forward");
  const [playerClass, setPlayerClass] = useState<number>(4);
  const [autoAvatar, setAutoAvatar] = useState<boolean>(true);

  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        setLoading(true);
        setError(null);
        const my = await getJSON<{ id: number }>("/api/my/club/");
        if (cancelled) return;
        setClubId(my.id);

        const list = await fetchPlayersRaw(my.id);
        if (cancelled) return;
        setBeforeIds(list.map((p) => p.id));
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Failed to load club data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const canSubmit = useMemo(
    () => !!clubId && !!position && playerClass >= 1 && playerClass <= 5 && !submitting,
    [clubId, position, playerClass, submitting]
  );

  async function handleSubmit() {
    if (!canSubmit || !clubId) return;
    try {
      setSubmitting(true);
      setError(null);
      setNotice("Creating player…");

      const url = `/clubs/${clubId}/create_player/?position=${encodeURIComponent(position)}&player_class=${playerClass}`;
      const res = await fetch(url, { method: "GET", credentials: "include" });
      if (!res.ok && res.status !== 302) {
        throw new Error(`Create request failed: ${res.status}`);
      }

      let lastTickText = "";
      const newId = await pollForNewPlayer(clubId, beforeIds, (i, max) => {
        const t = `Detecting new player (${i}/${max})`;
        if (t !== lastTickText) {
          setNotice(t);
          lastTickText = t;
        }
      });
      if (!newId) {
        setError("Не удалось определить ID нового игрока. Проверьте раздел Players вручную.");
        setSubmitting(false);
        setNotice(null);
        return;
      }

      if (autoAvatar) {
        setNotice("Generating avatar…");
        const csrf = getCsrfToken();
        try {
          await fetch(`/api/players/${newId}/generate-avatar/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...(csrf ? { "X-CSRFToken": csrf } : {}),
            },
            body: "{}",
            credentials: "include",
          });
        } catch {
          // не критично
        }
      }

      setNotice(null);
      navigate(`/player/overview?id=${newId}`);
    } catch (e: any) {
      setError(e?.message ?? "Create failed");
      setSubmitting(false);
      setNotice(null);
    }
  }

  const heroBadges = (
    <Stack direction="row" spacing={1} flexWrap="wrap">
      <Chip label="Cost зависит от класса" size="small" sx={{ color: "white", bgcolor: "rgba(255,255,255,0.12)" }} />
      <Chip label="Auto avatar создаёт портрет сразу" size="small" sx={{ color: "white", bgcolor: "rgba(255,255,255,0.12)" }} />
    </Stack>
  );

  const hero = (
    <HeroBar
      title="Create Player"
      subtitle="Generate new prospects for your squad"
      tone="pink"
      kpis={[
        { label: "Position", value: position, icon: <SportsSoccerIcon fontSize="small" /> },
        { label: "Class", value: `Class ${playerClass}`, icon: <MilitaryTechIcon fontSize="small" /> },
        { label: "Auto avatar", value: autoAvatar ? "ON" : "OFF", icon: <AutoFixHighIcon fontSize="small" /> },
        { label: "State", value: loading ? "Loading" : submitting ? "Submitting" : "Ready", icon: <QueryBuilderIcon fontSize="small" /> },
      ]}
      actions={
        <Button variant="contained" color="secondary" startIcon={<PersonAddAltIcon />} onClick={() => navigate("/my-club/players")}>
          Back to players
        </Button>
      }
    />
  );

  const topSection = (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Breadcrumbs>
            <Link to="/my-club">My Club</Link>
            <Link to="/my-club/players">Players</Link>
            <Typography variant="body2">Create</Typography>
          </Breadcrumbs>
          <Typography variant="body2" color="text.secondary">
            Выберите позицию и класс. После успешной генерации мы попробуем обнаружить нового игрока и открыть его профиль автоматически.
          </Typography>
          <Stack spacing={1}>
            <Typography variant="subtitle2">Советы</Typography>
            {heroBadges}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );

  const mainContent = (
    <Card>
      <CardContent>
        {error && (
          <Alert severity="error" className="mb-2">
            {error}
          </Alert>
        )}
        {notice && (
          <Alert severity="info" className="mb-2">
            {notice}
          </Alert>
        )}

        <Stack spacing={2}>
          <TextField
            select
            label="Position"
            value={position}
            onChange={(e) => setPosition(e.target.value)}
            disabled={loading || submitting}
            fullWidth
          >
            {POSITIONS.map((p) => (
              <MenuItem key={p} value={p}>
                {p}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Class"
            value={playerClass}
            onChange={(e) => setPlayerClass(Number(e.target.value))}
            disabled={loading || submitting}
            fullWidth
          >
            {[1, 2, 3, 4, 5].map((c) => (
              <MenuItem key={c} value={c}>
                Class {c}
              </MenuItem>
            ))}
          </TextField>

          <Divider />

          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Button variant="contained" color="primary" disableElevation disabled={!canSubmit} onClick={handleSubmit}>
              {submitting ? "Working…" : "Create"}
            </Button>
            <Button variant={autoAvatar ? "contained" : "outlined"} color="secondary" onClick={() => setAutoAvatar((v) => !v)} disabled={submitting}>
              {autoAvatar ? "Auto Avatar: ON" : "Auto Avatar: OFF"}
            </Button>
            <Button variant="outlined" disabled={submitting} onClick={() => navigate("/my-club/players")}>Cancel</Button>
          </Stack>

          <Typography variant="body2" color="text.secondary">
            • Стоимость списывается согласно классу. Если токенов не хватает, создание не произойдёт.
            <br />• После создания мы попытаемся автоматически определить ID и открыть профиль нового игрока.
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );

  const asideContent = (
    <Card>
      <CardContent>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Полезно знать
        </Typography>
        <Stack spacing={1}>
          <Typography variant="body2" color="text.secondary">
            • Class 1 — самый бюджетный вариант, Class 5 — дорогой, но с высоким потолком.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • Если ID не найден автоматически, проверьте список Players — там появится последняя запись.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • Auto Avatar можно выключить и загрузить портрет вручную позже.
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );

  return <PageShell hero={hero} top={topSection} main={mainContent} aside={asideContent} />;
}

