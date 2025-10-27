import { Button, Card, CardContent, Chip, Stack, Typography, Box } from "@mui/material";
import type { TransferListingDetail } from "@/types/transfers";
import { formatCurrency, formatDateTime, formatListingStatus, formatTimeRemaining } from "@/utils/transfers";

type SummaryCardProps = {
  detail: TransferListingDetail;
  busyKey: string | null;
  onMakeOffer?: () => void;
  onForceComplete?: () => void;
};

export function ListingSummaryCard({ detail, busyKey, onMakeOffer, onForceComplete }: SummaryCardProps) {
  const { listing, permissions } = detail;

  return (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h5" component="h2">
              Player
            </Typography>
            <Chip
              label={formatListingStatus(listing.status)}
              color={
                listing.status === "active"
                  ? "info"
                  : listing.status === "completed"
                  ? "success"
                  : listing.status === "cancelled"
                  ? "default"
                  : "warning"
              }
              size="small"
              variant="outlined"
            />
          </Stack>
          <Typography variant="h6">{listing.player.full_name}</Typography>
          <Typography variant="body2" color="text.secondary">
            {listing.player.position} · Age {listing.player.age} · Rating {listing.player.overall_rating}
          </Typography>
          <Typography variant="body2">Seller: {listing.club.name}</Typography>
          <Typography variant="body2">Asking Price: {formatCurrency(listing.asking_price)}</Typography>
          <Typography variant="body2">
            Highest Bid:{" "}
            {listing.summary.offers_count > 0 && listing.highest_bid
              ? formatCurrency(listing.highest_bid)
              : "No bids yet"}
          </Typography>
          <Typography variant="body2">
            Listed At: <strong>{formatDateTime(listing.listed_at)}</strong>
          </Typography>
          <Typography variant="body2">
            Expires At: <strong>{formatDateTime(listing.expires_at)}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Time Remaining: {formatTimeRemaining(listing.time_remaining)}
          </Typography>
          {listing.description && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Description
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {listing.description}
              </Typography>
            </Box>
          )}
          <Stack direction="row" spacing={1}>
            {listing.status === "active" && permissions.can_bid && (
              <Button variant="contained" onClick={onMakeOffer}>
                Make Offer
              </Button>
            )}
            {listing.status === "active" && permissions.can_accept_offers && (
              <Button
                variant="outlined"
                color="secondary"
                onClick={onForceComplete}
                disabled={busyKey === "expire-listing"}
              >
                {busyKey === "expire-listing" ? "Processing..." : "Force Complete"}
              </Button>
            )}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
