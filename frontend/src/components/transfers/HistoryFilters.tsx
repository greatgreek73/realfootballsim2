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
      <TextField label="Season ID" type="number" value={value.seasonId} onChange={handleField("seasonId")} />
      <TextField label="Club ID" type="number" value={value.clubId} onChange={handleField("clubId")} />
      <TextField label="Player ID" type="number" value={value.playerId} onChange={handleField("playerId")} />
      <Stack direction="row" spacing={1} alignItems="flex-start" sx={{ alignSelf: "flex-start" }}>
        <Button variant="outlined" onClick={onClear} disabled={loading}>
          Clear
        </Button>
        <Button variant="contained" onClick={onApply} disabled={loading}>
          Apply
        </Button>
      </Stack>
    </Stack>
  );
}
