import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";

import {
  acceptTransferOffer,
  cancelTransferOffer,
  fetchMyTransfersDashboard,
  rejectTransferOffer,
} from "@/api/transfers";
import { ListingTable } from "@/components/transfers/ListingTable";
import { OffersTable } from "@/components/transfers/OffersTable";
import { HistoryTable } from "@/components/transfers/HistoryTable";
import type { TransferClubDashboard, TransferOfferSummary } from "@/types/transfers";
import { formatCurrency } from "@/utils/transfers";

const EMPTY_META = { page: 1, totalPages: 1, count: 0, pageSize: 1 };

export default function MyClubTransfersPage() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<TransferClubDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ severity: "success" | "error" | "info"; message: string } | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchMyTransfersDashboard();
      setDashboard(response);
    } catch (err: any) {
      setError(err?.message ?? "Не удалось загрузить данные по трансферам клуба.");
      setDashboard(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const historyMeta = useMemo(() => {
    if (!dashboard) return EMPTY_META;
    return {
      page: 1,
      totalPages: 1,
      count: dashboard.history.length,
      pageSize: Math.max(dashboard.history.length, 1),
    };
  }, [dashboard]);

  const listingsMeta = useMemo(() => {
    if (!dashboard) return EMPTY_META;
    return {
      page: 1,
      totalPages: 1,
      count: dashboard.active_listings.length,
      pageSize: Math.max(dashboard.active_listings.length, 1),
    };
  }, [dashboard]);

  const runOfferAction = async (key: string, action: () => Promise<void>, message: string) => {
    setBusyKey(key);
    setFeedback(null);
    try {
      await action();
      await load();
      setFeedback({ severity: "success", message });
    } catch (err: any) {
      setFeedback({ severity: "error", message: err?.message ?? "Не удалось выполнить действие." });
    } finally {
      setBusyKey(null);
    }
  };

  const handleCancelOffer = (offer: TransferOfferSummary) =>
    runOfferAction(`cancel-${offer.id}`, () => cancelTransferOffer(offer.id), "Ставка отменена.");

  const handleAcceptOffer = (offer: TransferOfferSummary) =>
    runOfferAction(`accept-${offer.id}`, () => acceptTransferOffer(offer.id), "Ставка принята.");

  const handleRejectOffer = (offer: TransferOfferSummary) =>
    runOfferAction(`reject-${offer.id}`, () => rejectTransferOffer(offer.id), "Ставка отклонена.");

  return (
    <Box className="p-2 sm:p-4">
      <Stack direction={{ xs: "column", md: "row" }} spacing={2} justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="h1" component="h1" className="mb-0">
            Мои трансферы
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Управляйте активными листингами клуба, проверяйте входящие ставки и историю сделок.
          </Typography>
        </Box>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button variant="outlined" onClick={load} disabled={loading}>
            Обновить
          </Button>
          <Button variant="contained" onClick={() => navigate("/transfers/create")}>
            Выставить игрока
          </Button>
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
      ) : !dashboard ? (
        <Alert severity="info" className="mt-3">
          Данные клуба недоступны.
        </Alert>
      ) : (
        <Grid container spacing={3} className="mt-2">
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
                  <Typography variant="h5" component="h2">
                    Активные листинги
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Всего: {dashboard.active_listings.length}
                  </Typography>
                </Stack>
                <ListingTable
                  listings={dashboard.active_listings}
                  loading={loading}
                  pageMeta={listingsMeta}
                  onChangePage={() => undefined}
                  onView={(id) => navigate(`/transfers/${id}`)}
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
                  <Typography variant="h5" component="h2">
                    Входящие ставки
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Всего: {dashboard.pending_offers.length}
                  </Typography>
                </Stack>
                <OffersTable
                  offers={dashboard.pending_offers}
                  busyKey={busyKey}
                  onCancel={handleCancelOffer}
                  onAccept={handleAcceptOffer}
                  onReject={handleRejectOffer}
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h2" className="mb-3">
                  Игроки вне рынка
                </Typography>
                {dashboard.players_not_listed.length === 0 ? (
                  <Alert severity="info">Все игроки уже выставлены или недоступны.</Alert>
                ) : (
                  <List dense>
                    {dashboard.players_not_listed.map((player) => (
                      <ListItem key={player.id} disableGutters>
                        <ListItemText
                          primary={`${player.full_name} — ${player.position}, ${player.age} лет`}
                          secondary={`Базовая стоимость: ${formatCurrency(player.base_value)}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
                  <Typography variant="h5" component="h2">
                    История сделок клуба
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Последние: {dashboard.history.length}
                  </Typography>
                </Stack>
                <HistoryTable
                  entries={dashboard.history}
                  loading={loading}
                  pageMeta={historyMeta}
                  onChangePage={() => undefined}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
