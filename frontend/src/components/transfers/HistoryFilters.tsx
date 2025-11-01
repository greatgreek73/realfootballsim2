import { ChangeEvent } from "react";
import { Button, Stack, TextField } from "@mui/material";

export type HistoryFiltersState = {
  seasonId: string;
  clubId: string;
  playerId: string;
};

type HistoryFiltersProps = {
  value: HistoryFiltersState;
  onChange: (next: HistoryFiltersState) => void;
  onApply: () => void;
  onClear: () => void;
  loading?: boolean;
};

export function HistoryFilters({ value, onChange, onApply, onClear, loading }: HistoryFiltersProps) {
  const handleField =
    (field: keyof HistoryFiltersState) =>
    (event: ChangeEvent<HTMLInputElement>) =>
      onChange({ ...value, [field]: event.target.value });

  return (
    <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
      <Stack direction={{ xs: "column", md: "row" }} sx={{ gap: { xs: 1, md: 2 } }} flex={1}>
        <TextField label="Season ID" type="number" value={value.seasonId} onChange={handleField("seasonId")} />
        <TextField label="Club ID" type="number" value={value.clubId} onChange={handleField("clubId")} />
        <TextField label="Player ID" type="number" value={value.playerId} onChange={handleField("playerId")} />
      </Stack>
      <Stack direction="row" spacing={1} alignItems="flex-start" sx={{ alignSelf: { xs: "flex-start", md: "flex-start" } }}>
        <Button variant="outlined" onClick={onClear} disabled={loading} sx={{ height: 44 }}>
          Clear
        </Button>
        <Button variant="contained" onClick={onApply} disabled={loading} sx={{ height: 44 }}>
          Apply
        </Button>
      </Stack>
    </Stack>
  );
}
