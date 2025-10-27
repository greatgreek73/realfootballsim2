import { Button, Chip, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography, Alert } from "@mui/material";
import type { TransferOfferSummary } from "@/types/transfers";
import { formatCurrency, formatDateTime } from "@/utils/transfers";

type OffersTableProps = {
  offers: TransferOfferSummary[];
  onCancel: (offer: TransferOfferSummary) => void;
  onAccept: (offer: TransferOfferSummary) => void;
  onReject: (offer: TransferOfferSummary) => void;
  busyKey: string | null;
};

export function OffersTable({ offers, onCancel, onAccept, onReject, busyKey }: OffersTableProps) {
  if (offers.length === 0) {
    return <Alert severity="info">No offers yet. Be the first to submit a bid.</Alert>;
  }

  return (
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Bid</TableCell>
          <TableCell>Club</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Created</TableCell>
          <TableCell align="right">Actions</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {offers.map((offer) => (
          <TableRow key={offer.id} hover>
            <TableCell>{formatCurrency(offer.bid_amount)}</TableCell>
            <TableCell>
              <Stack spacing={0.25}>
                <Typography variant="body2">{offer.bidding_club.name}</Typography>
                {offer.is_own_offer && (
                  <Typography variant="caption" color="text.secondary">
                    Your club
                  </Typography>
                )}
              </Stack>
            </TableCell>
            <TableCell>
              <Stack direction="row" spacing={0.5} alignItems="center">
                <Chip label={offer.status} size="small" variant="outlined" />
                {offer.is_highest && <Chip label="Top Bid" color="success" size="small" variant="outlined" />}
              </Stack>
            </TableCell>
            <TableCell>{formatDateTime(offer.created_at)}</TableCell>
            <TableCell align="right">
              <Stack direction="row" spacing={1} justifyContent="flex-end">
                {offer.can_cancel && (
                  <Button
                    size="small"
                    onClick={() => onCancel(offer)}
                    disabled={busyKey === `cancel-${offer.id}`}
                  >
                    {busyKey === `cancel-${offer.id}` ? "Cancelling..." : "Cancel"}
                  </Button>
                )}
                {offer.can_accept && (
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => onAccept(offer)}
                    disabled={busyKey === `accept-${offer.id}`}
                  >
                    {busyKey === `accept-${offer.id}` ? "Accepting..." : "Accept"}
                  </Button>
                )}
                {offer.can_reject && (
                  <Button
                    size="small"
                    color="secondary"
                    onClick={() => onReject(offer)}
                    disabled={busyKey === `reject-${offer.id}`}
                  >
                    {busyKey === `reject-${offer.id}` ? "Rejecting..." : "Reject"}
                  </Button>
                )}
              </Stack>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
