import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import HomeWorkIcon from "@mui/icons-material/HomeWork";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";
import PersonAddAltIcon from "@mui/icons-material/PersonAddAlt";
import QueryStatsIcon from "@mui/icons-material/QueryStats";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { createTransferListing } from "@/api/transfers";
import type { TransferListingCreatePayload } from "@/types/transfers";
import { formatCurrency } from "@/utils/transfers";
import { getJSON } from "@/lib/apiClient";

type PlayerRow = {
  id: number;
  name: string;
  position?: string;
  age?: number;
  base_value?: number;
};

type ClubSummary = {
  id: number;
  name: string;
};

const DURATION_OPTIONS = [
  { value: 5, label: "5 minutes" },
  { value: 30, label: "30 minutes" },
  { value: 60, label: "60 minutes" },
];

export default function CreateTransferListingPage() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [club, setClub] = useState<ClubSummary | null>(null);
  const [players, setPlayers] = useState<PlayerRow[]>([]);

  const [playerId, setPlayerId] = useState<number | "">("");
  const [askingPrice, setAskingPrice] = useState("");
  const [duration, setDuration] = useState<number>(30);
  const [description, setDescription] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const myClub = await getJSON<{ id: number }>("/api/my/club/");
        if (!myClub?.id) {
          throw new Error("No club found for current user.");
        }
        const summary = await getJSON<ClubSummary>(`/api/clubs/${myClub.id}/summary/`);
        const roster = await getJSON<{ count: number; results: PlayerRow[] }>(
          `/api/clubs/${myClub.id}/players/`
        );

        if (!cancelled) {
          setClub(summary);
          setPlayers(roster?.results ?? []);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err?.message ?? "Failed to load club players.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (playerId === "") return;
    const selected = players.find((row) => row.id === playerId);
    if (selected && typeof selected.base_value === "number") {
      setAskingPrice(String(Math.max(selected.base_value, 0)));
    }
  }, [playerId, players]);

  const selectedPlayer = useMemo(() => {
    if (playerId === "") return null;
    return players.find((row) => row.id === playerId) ?? null;
  }, [playerId, players]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (playerId === "") {
      setError("Select a player to list.");
      return;
    }
    const price = Number(askingPrice);
    if (!Number.isFinite(price) || price <= 0) {
      setError("Enter a valid asking price.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const payload: TransferListingCreatePayload = {
        player_id: playerId,
        asking_price: Math.round(price),
        duration,
        description: description || undefined,
      };
      const response = await createTransferListing(payload);
      const newListingId = response?.listing?.id;
      if (newListingId) {
        navigate(`/transfers/${newListingId}`);
      } else {
        navigate("/transfers/my");
      }
    } catch (err: any) {
      setError(err?.message ?? "Failed to create listing.");
    } finally {
      setSubmitting(false);
    }
  };

  const hero = (
    <HeroBar
      title="Create Transfer Listing"
      subtitle="Подберите игрока, задайте цену и длительность аукциона"
      tone="green"
      kpis={[
        { label: "Club", value: club?.name ?? "—", icon: <HomeWorkIcon fontSize="small" /> },
        { label: "Roster", value: players.length || "0", icon: <PeopleAltIcon fontSize="small" /> },
        { label: "Selected", value: selectedPlayer?.name ?? "—", icon: <PersonAddAltIcon fontSize="small" /> },
        { label: "Status", value: loading ? "Loading" : error ? "Error" : "Ready", icon: <QueryStatsIcon fontSize="small" /> },
      ]}
      accent={
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {DURATION_OPTIONS.map((option) => (
            <Chip
              key={option.value}
              label={`Duration: ${option.label}`}
              size="small"
              sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
            />
          ))}
        </Stack>
      }
      actions={
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button variant="outlined" onClick={() => navigate("/transfers/my")}>
            My Deals
          </Button>
          <Button variant="contained" onClick={() => navigate("/transfers")}>
            Market
          </Button>
        </Stack>
      }
    />
  );

  const topSection = (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h2">
          List a Player
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Choose a player from your club, set the asking price and pick an auction duration.
        </Typography>
        {error && (
          <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
      </CardContent>
    </Card>
  );

  let mainContent: ReactNode;
  if (loading) {
    mainContent = (
      <Card>
        <CardContent>
          <Box className="flex w-full items-center justify-center p-6">
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  } else if (!club) {
    mainContent = (
      <Card>
        <CardContent>
          <Alert severity="warning">You need to own a club before listing players on the market.</Alert>
        </CardContent>
      </Card>
    );
  } else {
    mainContent = (
      <Card>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Stack spacing={3}>
              <Box>
                <Typography variant="subtitle1" color="text.secondary">
                  Club
                </Typography>
                <Typography variant="h6">{club.name}</Typography>
              </Box>

              <TextField
                select
                label="Player"
                value={playerId === "" ? "" : playerId}
                onChange={(event) => {
                  const value = event.target.value;
                  setPlayerId(value === "" ? "" : Number(value));
                }}
                required
                fullWidth
              >
                <MenuItem value="">
                  <em>Select player</em>
                </MenuItem>
                {players.map((player) => (
                  <MenuItem key={player.id} value={player.id}>
                    {player.name}
                    {player.position ? ` — ${player.position}` : ""}
                    {typeof player.age === "number" ? ` — Age ${player.age}` : ""}
                  </MenuItem>
                ))}
              </TextField>

              {selectedPlayer && (
                <Alert severity="info">
                  Current selection: <strong>{selectedPlayer.name}</strong>
                  {selectedPlayer.position ? ` (${selectedPlayer.position})` : ""}.{" "}
                  {typeof selectedPlayer.base_value === "number"
                    ? `Suggested minimum price: ${formatCurrency(selectedPlayer.base_value)}.`
                    : ""}
                </Alert>
              )}

              <TextField
                label="Asking Price"
                type="number"
                inputProps={{ min: selectedPlayer?.base_value ?? 0, step: 1 }}
                value={askingPrice}
                onChange={(event) => setAskingPrice(event.target.value)}
                required
                fullWidth
                helperText={
                  selectedPlayer && typeof selectedPlayer.base_value === "number"
                    ? `Minimum: ${formatCurrency(selectedPlayer.base_value)}`
                    : undefined
                }
              />

              <TextField
                select
                label="Auction Duration"
                value={duration}
                onChange={(event) => setDuration(Number(event.target.value))}
                fullWidth
              >
                {DURATION_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                label="Description"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                multiline
                minRows={3}
                placeholder="Add optional context or negotiation points."
              />

              <Stack direction="row" spacing={1} justifyContent="flex-end">
                <Button variant="outlined" onClick={() => navigate("/transfers")} disabled={submitting}>
                  Cancel
                </Button>
                <Button type="submit" variant="contained" disabled={submitting}>
                  {submitting ? "Submitting..." : "Create Listing"}
                </Button>
              </Stack>
            </Stack>
          </form>
        </CardContent>
      </Card>
    );
  }

  const asideContent: ReactNode | undefined =
    loading || !club
      ? undefined
      : (
          <Stack spacing={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Club summary
                </Typography>
                <Typography variant="body2">Name: {club.name}</Typography>
                <Typography variant="body2">Available players: {players.length}</Typography>
                <Typography variant="body2">
                  Selection: {selectedPlayer ? selectedPlayer.name : "None"}
                </Typography>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Auction durations
                </Typography>
                <Stack spacing={0.5}>
                  {DURATION_OPTIONS.map((option) => (
                    <Typography key={option.value} variant="body2">
                      {option.label}
                    </Typography>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </Stack>
        );

  return <PageShell hero={hero} top={topSection} main={mainContent} aside={asideContent} />;
}
