import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";
import Inventory2Icon from "@mui/icons-material/Inventory2";
import HandshakeIcon from "@mui/icons-material/Handshake";
import HistoryToggleOffIcon from "@mui/icons-material/HistoryToggleOff";
import PendingActionsIcon from "@mui/icons-material/PendingActions";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
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
      setError(err?.message ?? "Failed to load transfers dashboard.");
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
      setFeedback({ severity: "error", message: err?.message ?? "Failed to perform the requested action." });
    } finally {
      setBusyKey(null);
    }
  };

  const handleCancelOffer = (offer: TransferOfferSummary) =>
    runOfferAction(`cancel-${offer.id}`, () => cancelTransferOffer(offer.id), "Offer cancelled.");

  const handleAcceptOffer = (offer: TransferOfferSummary) =>
    runOfferAction(`accept-${offer.id}`, () => acceptTransferOffer(offer.id), "Offer accepted.");

  const handleRejectOffer = (offer: TransferOfferSummary) =>
    runOfferAction(`reject-${offer.id}`, () => rejectTransferOffer(offer.id), "Offer rejected.");

  const heroActions = (
    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
      <Button variant="outlined" onClick={load} disabled={loading}>
        Refresh
      </Button>
      <Button variant="contained" onClick={() => navigate("/transfers/create")}>
        Create Listing
      </Button>
    </Stack>
  );

  const heroSummary =
    dashboard && (
      <Stack direction="row" spacing={1} flexWrap="wrap">
        <Chip
          label={`Players to list: ${dashboard.players_not_listed.length}`}
          size="small"
          sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
        />
        <Chip
          label={`Offers pending: ${dashboard.pending_offers.length}`}
          size="small"
          sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
        />
      </Stack>
    );

  const hero = (
    <HeroBar
      title="My Transfers"
      subtitle="Управляйте объявлениями клуба и входящими предложениями"
      tone="purple"
      kpis={[
        {
          label: "Listings",
          value: dashboard ? dashboard.active_listings.length : "—",
          icon: <Inventory2Icon fontSize="small" />,
        },
        {
          label: "Offers",
          value: dashboard ? dashboard.pending_offers.length : "—",
          icon: <HandshakeIcon fontSize="small" />,
        },
        {
          label: "History",
          value: dashboard ? dashboard.history.length : "—",
          icon: <HistoryToggleOffIcon fontSize="small" />,
        },
        {
          label: "Status",
          value: loading ? "Loading" : error ? "Error" : "Ready",
          icon: <PendingActionsIcon fontSize="small" />,
        },
      ]}
      actions={heroActions}
    />
  );

  const topSection = (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Box>
            <Typography variant="h5" component="h1" gutterBottom>
              My Transfers Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Track your listings, incoming offers, and recent transfer history.
            </Typography>
            {heroSummary && (
              <Stack spacing={1} mt={1.5}>
                <Typography variant="subtitle2">Snapshot</Typography>
                {heroSummary}
              </Stack>
            )}
          </Box>
          {feedback && (
            <Alert severity={feedback.severity} onClose={() => setFeedback(null)}>
              {feedback.message}
            </Alert>
          )}
          {error && <Alert severity="error">{error}</Alert>}
        </Stack>
      </CardContent>
    </Card>
  );

  let mainContent: ReactNode;
  if (loading) {
    mainContent = (
      <Card>
        <CardContent>
          <Box className="flex w-full items-center justify-center p-6">
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  } else if (!dashboard) {
    mainContent = <Alert severity="info">No transfer data available.</Alert>;
  } else {
    mainContent = (
      <Stack spacing={3}>
        <Card>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
              <Typography variant="h5" component="h2">
                Active Listings
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total: {dashboard.active_listings.length}
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

        <Card>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
              <Typography variant="h5" component="h2">
                Pending Offers
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total: {dashboard.pending_offers.length}
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
      </Stack>
    );
  }

  const asideContent: ReactNode | undefined =
    loading || !dashboard
      ? undefined
      : (
          <Stack spacing={3}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h2" className="mb-3">
                  Players You Can List
                </Typography>
                {dashboard.players_not_listed.length === 0 ? (
                  <Alert severity="info">All players are already listed or unavailable.</Alert>
                ) : (
                  <List dense>
                    {dashboard.players_not_listed.map((player) => (
                      <ListItem key={player.id} disableGutters>
                        <ListItemText
                          primary={`${player.full_name} - ${player.position}, ${player.age} y.o.`}
                          secondary={`Estimated value: ${formatCurrency(player.base_value)}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
                  <Typography variant="h5" component="h2">
                    Club Transfer History
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Entries: {dashboard.history.length}
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
          </Stack>
        );

  return <PageShell hero={hero} top={topSection} main={mainContent} aside={asideContent} />;
}
