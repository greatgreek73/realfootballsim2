import { FormEvent, useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  FormControlLabel,
  IconButton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

import { createMatch } from "@/api/matches";

function toLocalInputValue(date: Date) {
  const iso = date.toISOString();
  return iso.slice(0, 16);
}

export default function MatchCreatePage() {
  const navigate = useNavigate();

  const [homeTeamId, setHomeTeamId] = useState("");
  const [awayTeamId, setAwayTeamId] = useState("");
  const [datetimeLocal, setDatetimeLocal] = useState("");
  const [autoOpponent, setAutoOpponent] = useState(true);
  const [autoStart, setAutoStart] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUseNow = () => {
    setDatetimeLocal(toLocalInputValue(new Date()));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitting) return;

    const homeId = Number(homeTeamId);
    const awayId = Number(awayTeamId);
    const payload: {
      homeTeamId?: number;
      awayTeamId?: number;
      datetime?: string;
      autoOpponent?: boolean;
      autoStart?: boolean;
    } = {
      autoOpponent,
      autoStart,
    };

    if (Number.isFinite(homeId) && homeId > 0) {
      payload.homeTeamId = homeId;
    }
    if (!autoOpponent && (!Number.isFinite(awayId) || awayId <= 0)) {
      setError("Enter a valid away team ID or enable auto opponent.");
      return;
    }
    if (Number.isFinite(awayId) && awayId > 0) {
      payload.awayTeamId = awayId;
    }

    if (datetimeLocal) {
      const parsed = new Date(datetimeLocal);
      if (Number.isNaN(parsed.getTime())) {
        setError("Provide a valid kickoff datetime.");
        return;
      }
      payload.datetime = parsed.toISOString();
    }

    try {
      setSubmitting(true);
      setError(null);
      const match = await createMatch(payload);
      navigate(`/matches/${match.id}`);
    } catch (e: any) {
      setError(e?.message ?? "Failed to schedule match");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 4 } }}>
      <Stack spacing={3}>
        <Stack direction="row" spacing={1} alignItems="center">
          <IconButton component={RouterLink} to="/matches" color="primary">
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h1" component="h1" className="mb-0">
            Schedule Match
          </Typography>
        </Stack>

        {error && <Alert severity="warning">{error}</Alert>}

        <Card>
          <CardContent>
            <Typography variant="h5" component="h2" className="mb-3">
              Match Parameters
            </Typography>
            <Stack component="form" spacing={3} onSubmit={handleSubmit}>
              <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                <TextField
                  label="Home team ID"
                  type="number"
                  value={homeTeamId}
                  onChange={(event) => setHomeTeamId(event.target.value)}
                  helperText="Leave empty to use your club (if available)."
                  fullWidth
                />
                <TextField
                  label="Away team ID"
                  type="number"
                  value={awayTeamId}
                  onChange={(event) => setAwayTeamId(event.target.value)}
                  helperText={autoOpponent ? "Ignored when auto opponent is enabled." : "Required when auto opponent is off."}
                  disabled={autoOpponent}
                  fullWidth
                />
              </Stack>

              <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                <TextField
                  label="Kickoff time"
                  type="datetime-local"
                  value={datetimeLocal}
                  onChange={(event) => setDatetimeLocal(event.target.value)}
                  InputLabelProps={{ shrink: true }}
                  helperText="Defaults to now when left empty."
                  fullWidth
                />
                <Button variant="outlined" onClick={handleUseNow} sx={{ alignSelf: { xs: "stretch", md: "center" }, minWidth: 160 }}>
                  Use current time
                </Button>
              </Stack>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={autoOpponent}
                    onChange={(event) => setAutoOpponent(event.target.checked)}
                  />
                }
                label="Pick automatic opponent (prefer bots)"
              />

              <FormControlLabel
                control={
                  <Checkbox
                    checked={autoStart}
                    onChange={(event) => setAutoStart(event.target.checked)}
                  />
                }
                label="Start match immediately after scheduling"
              />

              <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                <Button type="submit" variant="contained" disabled={submitting}>
                  {submitting ? "Scheduling..." : "Create Match"}
                </Button>
                <Button variant="text" component={RouterLink} to="/matches">
                  Cancel
                </Button>
              </Stack>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}
