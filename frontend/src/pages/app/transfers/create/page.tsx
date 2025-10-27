import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

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
          `/api/clubs/${myClub.id}/players/`,
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
        navigate("/transfers");
      }
    } catch (err: any) {
      let message = err?.message ?? "Failed to create listing.";
      const jsonPart = message.match(/-\s({.+})$/);
      if (jsonPart) {
        try {
          const body = JSON.parse(jsonPart[1]);
          if (body?.errors) {
            const flattened = Object.values(body.errors)
              .flat()
              .join(" ");
            if (flattened) {
              message = flattened;
            }
          } else if (body?.detail) {
            message = body.detail;
          }
        } catch {
          /* ignore parse errors */
        }
      }
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box className="p-2 sm:p-4">
      <Stack spacing={1}>
        <Typography variant="h1" component="h1">
          List a Player
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Choose a player from your club and set the asking price and auction duration.
        </Typography>
      </Stack>

      {error && (
        <Alert severity="error" className="mt-3" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box className="flex w-full items-center justify-center p-6">
          <CircularProgress />
        </Box>
      ) : !club ? (
        <Alert severity="warning" className="mt-3">
          You need to own a club before listing players on the market.
        </Alert>
      ) : (
        <Card className="mt-3">
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
                      {player.position ? ` · ${player.position}` : ""}
                      {typeof player.age === "number" ? ` · Age ${player.age}` : ""}
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
      )}
    </Box>
  );
}
