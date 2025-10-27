import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Alert, AlertColor, Box, Button, Card, CardContent, CircularProgress, Grid, Stack, Typography } from "@mui/material";

import {
  acceptTransferOffer,
  cancelTransferListing,
  cancelTransferOffer,
  createTransferOffer,
  expireTransferListing,
  fetchTransferListing,
  rejectTransferOffer,
} from "@/api/transfers";
import { OfferDialog, OfferDialogState } from "@/components/transfers/OfferDialog";
import { OffersTable } from "@/components/transfers/OffersTable";
import { ListingSummaryCard } from "@/components/transfers/ListingSummaryCard";
import type { TransferListingDetail, TransferOfferSummary } from "@/types/transfers";

const INITIAL_DIALOG_STATE: OfferDialogState = {
  open: false,
  bidAmount: "",
  message: "",
  submitting: false,
};

export default function TransferListingDetailPage() {
  const params = useParams();
  const listingId = Number(params.listingId);
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<TransferListingDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ severity: AlertColor; message: string } | null>(null);
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [dialogState, setDialogState] = useState<OfferDialogState>(INITIAL_DIALOG_STATE);

  const listing = detail?.listing;
  const offers = detail?.offers ?? [];
  const permissions = detail?.permissions ?? {
    is_owner: false,
    can_bid: false,
    can_cancel_listing: false,
    can_accept_offers: false,
  };

  const highestBid = useMemo(() => listing?.highest_bid ?? null, [listing]);

  const loadListing = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchTransferListing(listingId);
      setDetail(response);
    } catch (err: any) {
      setError(err?.message ?? "Не удалось загрузить данные листинга.");
      setDetail(null);
    } finally {
      setLoading(false);
    }
  }, [listingId]);

  useEffect(() => {
    if (!Number.isFinite(listingId)) {
      setError("Некорректный идентификатор листинга.");
      setLoading(false);
      return;
    }
    void loadListing();
  }, [loadListing, listingId]);

  const runWithBusyState = async (key: string, action: () => Promise<void>, successMessage?: string) => {
    setBusyKey(key);
    setFeedback(null);
    try {
      await action();
      await loadListing();
      if (successMessage) {
        setFeedback({ severity: "success", message: successMessage });
      }
    } catch (err: any) {
      setFeedback({ severity: "error", message: err?.message ?? "Не удалось выполнить действие." });
    } finally {
      setBusyKey(null);
    }
  };

  const handleCancelListing = () =>
    runWithBusyState("cancel-listing", () => cancelTransferListing(listingId), "Листинг отменён.");

  const handleExpireListing = () =>
    runWithBusyState("expire-listing", () => expireTransferListing(listingId), "Листинг обновлён.");

  const openOfferDialog = () =>
    setDialogState({
      open: true,
      bidAmount: highestBid ? String(highestBid) : listing ? String(listing.asking_price) : "",
      message: "",
      submitting: false,
    });

  const submitOffer = async () => {
    if (!listing) return;
    const amount = Number(dialogState.bidAmount);
    if (!Number.isFinite(amount) || amount <= 0) {
      setFeedback({ severity: "warning", message: "Введите корректную сумму ставки." });
      return;
    }

    setDialogState((prev) => ({ ...prev, submitting: true }));
    try {
      await createTransferOffer(listing.id, {
        bid_amount: Math.round(amount),
        message: dialogState.message || undefined,
      });
      setDialogState(INITIAL_DIALOG_STATE);
      await loadListing();
      setFeedback({ severity: "success", message: "Ставка отправлена." });
    } catch (err: any) {
      setFeedback({ severity: "error", message: err?.message ?? "Не удалось отправить ставку." });
      setDialogState((prev) => ({ ...prev, submitting: false }));
    }
  };

  const handleOfferAction = (offer: TransferOfferSummary, action: "cancel" | "reject" | "accept") => {
    const key = `${action}-${offer.id}`;
    runWithBusyState(
      key,
      () =>
        action === "cancel"
          ? cancelTransferOffer(offer.id)
          : action === "reject"
          ? rejectTransferOffer(offer.id)
          : acceptTransferOffer(offer.id),
      action === "accept" ? "Ставка принята." : action === "cancel" ? "Ставка отменена." : "Ставка отклонена."
    );
  };

  if (!Number.isFinite(listingId)) {
    return (
      <Box className="p-4">
        <Alert severity="error">Некорректный идентификатор листинга.</Alert>
      </Box>
    );
  }

  return (
    <Box className="p-2 sm:p-4">
      <Stack direction={{ xs: "column", md: "row" }} spacing={2} justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="h1" component="h1" className="mb-0">
            Листинг трансфера
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Просмотр деталей, ставок и доступных действий.
          </Typography>
        </Box>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button variant="outlined" onClick={() => navigate("/transfers")}>
            Назад к рынку
          </Button>
          {listing?.status === "active" && permissions.can_cancel_listing && (
            <Button
              variant="contained"
              color="secondary"
              onClick={handleCancelListing}
              disabled={busyKey === "cancel-listing"}
            >
              {busyKey === "cancel-listing" ? "Отмена..." : "Отменить листинг"}
            </Button>
          )}
        </Stack>
      </Stack>

      {feedback && (
        <Alert severity={feedback.severity} className="mt-3" onClose={() => setFeedback(null)}>
          {feedback.message}
        </Alert>
      )}

      {error && (
        <Alert severity="error" className="mt-3">
          {error}
        </Alert>
      )}

      {loading ? (
        <Box className="flex w-full items-center justify-center p-6">
          <CircularProgress />
        </Box>
      ) : detail && listing ? (
        <Grid container spacing={3} className="mt-2">
          <Grid item xs={12} lg={4}>
            <ListingSummaryCard
              detail={detail}
              busyKey={busyKey}
              onMakeOffer={openOfferDialog}
              onForceComplete={handleExpireListing}
            />
          </Grid>
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
                  <Typography variant="h5" component="h2">
                    Ставки
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Всего: {offers.length}
                  </Typography>
                </Stack>
                <OffersTable
                  offers={offers}
                  busyKey={busyKey}
                  onCancel={(offer) => handleOfferAction(offer, "cancel")}
                  onReject={(offer) => handleOfferAction(offer, "reject")}
                  onAccept={(offer) => handleOfferAction(offer, "accept")}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        !error && (
          <Box className="p-4">
            <Alert severity="info">Листинг не найден или недоступен.</Alert>
          </Box>
        )
      )}

      <OfferDialog
        state={dialogState}
        setState={setDialogState}
        onSubmit={submitOffer}
        minAmount={listing?.asking_price}
      />
    </Box>
  );
}
