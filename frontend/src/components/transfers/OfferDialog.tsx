import { Dispatch, SetStateAction } from "react";
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Stack, TextField } from "@mui/material";

export type OfferDialogState = {
  open: boolean;
  bidAmount: string;
  message: string;
  submitting: boolean;
};

type OfferDialogProps = {
  state: OfferDialogState;
  setState: Dispatch<SetStateAction<OfferDialogState>>;
  onSubmit: () => void;
  minAmount?: number;
};

export function OfferDialog({ state, setState, onSubmit, minAmount }: OfferDialogProps) {
  const handleClose = () =>
    setState({
      open: false,
      bidAmount: "",
      message: "",
      submitting: false,
    });

  return (
    <Dialog open={state.open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle>Submit Offer</DialogTitle>
      <DialogContent>
        <Stack spacing={2} mt={1}>
          <TextField
            label="Bid Amount"
            type="number"
            value={state.bidAmount}
            onChange={(event) => setState((prev) => ({ ...prev, bidAmount: event.target.value }))}
            inputProps={{ min: minAmount ?? 0, step: 1 }}
            required
            autoFocus
          />
          <TextField
            label="Message (optional)"
            value={state.message}
            onChange={(event) => setState((prev) => ({ ...prev, message: event.target.value }))}
            multiline
            minRows={2}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={state.submitting}>
          Close
        </Button>
        <Button variant="contained" onClick={onSubmit} disabled={state.submitting}>
          {state.submitting ? "Submitting..." : "Submit Offer"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
