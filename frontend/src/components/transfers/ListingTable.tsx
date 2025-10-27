import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Pagination,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import type { TransferListingSummary } from "@/types/transfers";
import { formatCurrency, formatDateTime, formatListingStatus, formatTimeRemaining } from "@/utils/transfers";

export type ListingsPageMeta = {
  page: number;
  totalPages: number;
  count: number;
  pageSize: number;
};

type ListingTableProps = {
  listings: TransferListingSummary[];
  loading: boolean;
  pageMeta: ListingsPageMeta;
  onChangePage: (page: number) => void;
  onView: (listingId: number) => void;
};

export function ListingTable({ listings, loading, pageMeta, onChangePage, onView }: ListingTableProps) {
  return (
    <>
      {loading && listings.length === 0 ? (
        <Box className="flex w-full items-center justify-center p-6">
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer>
          <Table size="medium">
            <TableHead>
              <TableRow>
                <TableCell>Player</TableCell>
                <TableCell>Club</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Highest Bid</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Expires</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {listings.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No listings match the current filters.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                listings.map((listing) => {
                  const statusLabel = formatListingStatus(listing.status);
                  return (
                    <TableRow key={listing.id} hover>
                      <TableCell>
                        <Stack spacing={0.25}>
                          <Typography variant="body2" fontWeight={600}>
                            {listing.player.full_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {listing.player.position} · Age {listing.player.age} · Rating {listing.player.overall_rating}
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{listing.club.name}</Typography>
                      </TableCell>
                      <TableCell>{formatCurrency(listing.asking_price)}</TableCell>
                      <TableCell>
                        {listing.highest_bid ? (
                          formatCurrency(listing.highest_bid)
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            No bids yet
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={statusLabel}
                          color={
                            listing.status === "active"
                              ? "info"
                              : listing.status === "completed"
                              ? "success"
                              : listing.status === "cancelled"
                              ? "default"
                              : "warning"
                          }
                          variant="outlined"
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Stack spacing={0.25}>
                          <Typography variant="body2">{formatDateTime(listing.expires_at)}</Typography>
                          {listing.status === "active" && (
                            <Typography variant="caption" color="text.secondary">
                              {formatTimeRemaining(listing.time_remaining)}
                            </Typography>
                          )}
                        </Stack>
                      </TableCell>
                      <TableCell align="right">
                        <Button size="small" onClick={() => onView(listing.id)}>
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Stack direction="row" justifyContent="space-between" alignItems="center" mt={3}>
        <Typography variant="body2" color="text.secondary">
          Page Size: {pageMeta.pageSize}
        </Typography>
        <Pagination
          count={pageMeta.totalPages}
          page={pageMeta.page}
          onChange={(_, newPage) => onChangePage(newPage)}
          color="primary"
          shape="rounded"
          showFirstButton
          showLastButton
        />
      </Stack>
    </>
  );
}
