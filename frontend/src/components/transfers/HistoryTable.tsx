import {
  Box,
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
import type { TransferHistoryEntry } from "@/types/transfers";
import { formatCurrency, formatDateTime } from "@/utils/transfers";

export type HistoryPageMeta = {
  page: number;
  totalPages: number;
  count: number;
};

type HistoryTableProps = {
  entries: TransferHistoryEntry[];
  loading: boolean;
  pageMeta: HistoryPageMeta;
  onChangePage: (page: number) => void;
};

export function HistoryTable({ entries, loading, pageMeta, onChangePage }: HistoryTableProps) {
  return (
    <>
      {loading && entries.length === 0 ? (
        <Box className="flex w-full items-center justify-center p-6">
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer>
          <Table size="medium">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Player</TableCell>
                <TableCell>From</TableCell>
                <TableCell>To</TableCell>
                <TableCell align="right">Fee</TableCell>
                <TableCell>Season</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {entries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No transfers in the selected range.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{formatDateTime(entry.transfer_date)}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {entry.player.full_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {entry.player.position}
                      </Typography>
                    </TableCell>
                    <TableCell>{entry.from_club?.name ?? "—"}</TableCell>
                    <TableCell>{entry.to_club?.name ?? "—"}</TableCell>
                    <TableCell align="right">{formatCurrency(entry.transfer_fee)}</TableCell>
                    <TableCell>{entry.season?.name ?? "—"}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Stack direction="row" justifyContent="center" mt={3}>
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
