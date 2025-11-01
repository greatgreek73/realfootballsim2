import { Grid, MenuItem, Stack, TextField, Button } from "@mui/material";
import type { TransferListingStatus } from "@/types/transfers";
import type { ChangeEvent } from "react";

export type ListingFiltersState = {
  position: string;
  minAge: string;
  maxAge: string;
  minPrice: string;
  maxPrice: string;
  status: TransferListingStatus | "";
};

type ListingFiltersProps = {
  value: ListingFiltersState;
  onChange: (next: ListingFiltersState) => void;
  onApply: () => void;
  onClear: () => void;
  loading?: boolean;
};

const POSITION_OPTIONS = [
  { value: "", label: "All Positions" },
  { value: "Goalkeeper", label: "Goalkeeper" },
  { value: "Right Back", label: "Right Back" },
  { value: "Left Back", label: "Left Back" },
  { value: "Center Back", label: "Center Back" },
  { value: "Defensive Midfielder", label: "Defensive Midfielder" },
  { value: "Right Midfielder", label: "Right Midfielder" },
  { value: "Central Midfielder", label: "Central Midfielder" },
  { value: "Left Midfielder", label: "Left Midfielder" },
  { value: "Attacking Midfielder", label: "Attacking Midfielder" },
  { value: "Center Forward", label: "Center Forward" },
];

const STATUS_OPTIONS: Array<{ value: TransferListingStatus | ""; label: string }> = [
  { value: "", label: "All Statuses" },
  { value: "active", label: "Active" },
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
  { value: "expired", label: "Expired" },
];

export function ListingFilters({ value, onChange, onApply, onClear, loading }: ListingFiltersProps) {
  const handleFieldChange =
    (field: keyof ListingFiltersState) =>
    (event: ChangeEvent<HTMLInputElement>) => {
      onChange({ ...value, [field]: event.target.value });
    };

  return (
    <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ xs: "stretch", md: "flex-start" }}>
      <Grid container spacing={2} flex={1}>
        <Grid item xs={12} sm={6} md={4}>
          <TextField
            select
            label="Position"
            value={value.position}
            onChange={handleFieldChange("position")}
            fullWidth
            sx={{ minWidth: { md: 260 } }}
          >
            {POSITION_OPTIONS.map((option) => (
              <MenuItem key={option.value || "all"} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={6} sm={3} md={3}>
          <TextField
            label="Min Age"
            type="number"
            inputProps={{ min: 16, max: 45 }}
            value={value.minAge}
            onChange={handleFieldChange("minAge")}
            fullWidth
          />
        </Grid>
        <Grid item xs={6} sm={3} md={3}>
          <TextField
            label="Max Age"
            type="number"
            inputProps={{ min: 16, max: 45 }}
            value={value.maxAge}
            onChange={handleFieldChange("maxAge")}
            fullWidth
          />
        </Grid>
        <Grid item xs={6} sm={3} md={2} sx={{ maxWidth: { md: 180 } }}>
          <TextField
            label="Min Price"
            type="number"
            inputProps={{ min: 0, max: 10000000000, inputMode: "numeric", pattern: "[0-9]*" }}
            value={value.minPrice}
            onChange={handleFieldChange("minPrice")}
            fullWidth
          />
        </Grid>
        <Grid item xs={6} sm={3} md={2} sx={{ maxWidth: { md: 180 } }}>
          <TextField
            label="Max Price"
            type="number"
            inputProps={{ min: 0, max: 10000000000, inputMode: "numeric", pattern: "[0-9]*" }}
            value={value.maxPrice}
            onChange={handleFieldChange("maxPrice")}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            select
            label="Status"
            value={value.status}
            onChange={handleFieldChange("status")}
            fullWidth
            sx={{ minWidth: { md: 200 } }}
          >
            {STATUS_OPTIONS.map((option) => (
              <MenuItem key={option.value || "all"} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
      </Grid>
      <Stack direction="row" spacing={1.5} alignItems="flex-start" sx={{ alignSelf: { xs: "flex-start", md: "flex-start" } }}>
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
