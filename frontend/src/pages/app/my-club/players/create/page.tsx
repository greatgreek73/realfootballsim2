import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Breadcrumbs,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
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
  const m = document.cookie.match(/(^|;\s*)csrftoken=([^;]+)/);
  return m ? decodeURIComponent(m[2]) : undefined;
}

/** Надёжный считыватель списка игроков без кэша */
async function fetchPlayersRaw(clubId: number): Promise<ApiPlayer[]> {
  const url = `/api/clubs/${clubId}/players/?_=${Date.now()}`;
  const res = await fetch(url, { credentials: "include", cache: "no-store" });
  if (!res.ok) throw new Error(`Players fetch failed: ${res.status}`);
  const data = await res.json();
  // Поддерживаем два варианта: {count, results} ИЛИ просто массив
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
        // Берём самый большой как наиболее новый
        diff.sort((a, b) => b - a);
        return diff[0];
      }
    } catch {
      // глотать и пробовать дальше
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
  const [autoAvatar, setAutoAvatar] = useState<boolean>(true); // генерировать аватар после создания

  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // Загружаем id моего клуба и «снимок» списка игроков ДО создания
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        setLoading(true);
        setError(null);

        // 1) Мой клуб
        const my = await getJSON<{ id: number }>("/api/my/club/");
        if (cancelled) return;
        setClubId(my.id);

        // 2) Текущий список игроков (для диффа)
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

  /** Сабмит: вызвать бэкенд, найти нового игрока, сгенерить аватар (по желанию), перейти в профиль */
  async function handleSubmit() {
    if (!canSubmit || !clubId) return;
    try {
      setSubmitting(true);
      setError(null);
      setNotice("Creating player…");

      // 1) Создание игрока — через Vite proxy (без CORS)
      const url = `/clubs/${clubId}/create_player/?position=${encodeURIComponent(
        position
      )}&player_class=${playerClass}`;
      const res = await fetch(url, { method: "GET", credentials: "include" });
      if (!res.ok && res.status !== 302) {
        throw new Error(`Create request failed: ${res.status}`);
      }

      // 2) Получаем ID нового игрока
      let lastTickText = "";
      const newId = await pollForNewPlayer(clubId, beforeIds, (i, max) => {
        const t = `Detecting new player… (${i}/${max})`;
        if (t !== lastTickText) {
          setNotice(t);
          lastTickText = t;
        }
      });
      if (!newId) {
        setError(
          "Не удалось определить ID нового игрока. Проверьте, что списались токены, и обновите список Players."
        );
        setSubmitting(false);
        setNotice(null);
        return;
      }

      // 3) Генерация аватара (если включено)
      if (autoAvatar) {
        setNotice("Generating avatar…");
        const csrf = getCsrfToken();
        try {
          const avatarRes = await fetch(`/api/players/${newId}/generate-avatar/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...(csrf ? { "X-CSRFToken": csrf } : {}),
            },
            body: "{}",
            credentials: "include",
          });
          // игнорируем статус, если на сервере отключено
          if (!avatarRes.ok) {
            // не ломаем поток — просто продолжаем
          }
        } catch {
          // тоже не критично
        }
      }

      // 4) Переход на страницу игрока
      setNotice(null);
      navigate(`/player/overview?id=${newId}`);
    } catch (e: any) {
      setError(e?.message ?? "Create failed");
      setSubmitting(false);
      setNotice(null);
    }
  }

  return (
    <Grid container spacing={5} className="w-full" size={12}>
      <Grid size={12}>
        <Typography variant="h1" component="h1" className="mb-0">
          Create Player
        </Typography>
        <Breadcrumbs>
          <Link to="/my-club">My Club</Link>
          <Link to="/my-club/players">Players</Link>
          <Typography variant="body2">Create</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={{ md: 6, xs: 12 }}>
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

              <Stack direction="row" spacing={1}>
                <Button
                  variant="contained"
                  color="primary"
                  disableElevation
                  disabled={!canSubmit}
                  onClick={handleSubmit}
                >
                  {submitting ? "Working…" : "Create"}
                </Button>
                <Button
                  variant={autoAvatar ? "contained" : "outlined"}
                  color="secondary"
                  onClick={() => setAutoAvatar((v) => !v)}
                  disabled={submitting}
                >
                  {autoAvatar ? "Auto Avatar: ON" : "Auto Avatar: OFF"}
                </Button>
                <Button
                  variant="outlined"
                  disabled={submitting}
                  onClick={() => navigate("/my-club/players")}
                >
                  Back to Players
                </Button>
              </Stack>

              <Typography variant="body2" color="text.secondary">
                • Стоимость списывается согласно классу. Если токенов недостаточно — создание не произойдёт. <br />
                • После создания будет открыт профиль нового игрока; при включённом Auto Avatar запустится генерация аватара.
              </Typography>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
