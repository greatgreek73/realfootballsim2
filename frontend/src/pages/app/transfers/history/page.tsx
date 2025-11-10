import { ReactNode, useEffect, useMemo, useState } from "react";
import { Link as RouterLink, useSearchParams } from "react-router-dom";

import { Alert, Button, Card, CardContent, Chip, Stack, Typography } from "@mui/material";
import HistoryEduIcon from "@mui/icons-material/HistoryEdu";
import QueryStatsIcon from "@mui/icons-material/QueryStats";
import FilterAltIcon from "@mui/icons-material/FilterAlt";
import TimelineIcon from "@mui/icons-material/Timeline";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { fetchTransferHistory } from "@/api/transfers";
import { HistoryFilters, HistoryFiltersState } from "@/components/transfers/HistoryFilters";
import { HistoryTable, HistoryPageMeta } from "@/components/transfers/HistoryTable";
import type { TransferHistoryEntry, TransferHistoryParams } from "@/types/transfers";

const DEFAULT_FILTERS: HistoryFiltersState = {
  seasonId: "",
  clubId: "",
  playerId: "",
};

export default function TransferHistoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState<HistoryFiltersState>(() => ({
    seasonId: searchParams.get("season_id") ?? "",
    clubId: searchParams.get("club_id") ?? "",
    playerId: searchParams.get("player_id") ?? "",
  }));

  const [records, setRecords] = useState<TransferHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pageMeta, setPageMeta] = useState<HistoryPageMeta>({
    page: 1,
    totalPages: 1,
    count: 0,
  });

  const page = useMemo(() => {
    const parsed = parseInt(searchParams.get("page") ?? "1", 10);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
  }, [searchParams]);

  useEffect(() => {
    setFilters({
      seasonId: searchParams.get("season_id") ?? "",
      clubId: searchParams.get("club_id") ?? "",
      playerId: searchParams.get("player_id") ?? "",
    });
  }, [searchParams]);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const params: TransferHistoryParams = {
          page,
          ordering: "-transfer_date",
        };
        const seasonId = searchParams.get("season_id");
        const clubId = searchParams.get("club_id");
        const playerId = searchParams.get("player_id");

        if (seasonId) params.seasonId = Number(seasonId);
        if (clubId) params.clubId = Number(clubId);
        if (playerId) params.playerId = Number(playerId);

        const response = await fetchTransferHistory(params);
        if (!controller.signal.aborted) {
          setRecords(response.results);
          setPageMeta({
            page: response.page,
            totalPages: Math.max(response.total_pages, 1),
            count: response.count,
          });
        }
      } catch (err: any) {
        if (!controller.signal.aborted) {
          setError(err?.message ?? "Failed to load transfer history.");
          setRecords([]);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void load();
    return () => controller.abort();
  }, [page, searchParams]);

  const updateSearchParams = (updates: Record<string, string | null>) => {
    const next = new URLSearchParams(searchParams);
    Object.entries(updates).forEach(([key, value]) => {
      if (!value) {
        next.delete(key);
      } else {
        next.set(key, value);
      }
    });
    setSearchParams(next);
  };

  const handleApplyFilters = () => {
    updateSearchParams({
      season_id: filters.seasonId || null,
      club_id: filters.clubId || null,
      player_id: filters.playerId || null,
      page: "1",
    });
  };

  const handleClearFilters = () => {
    setFilters(DEFAULT_FILTERS);
    updateSearchParams({
      season_id: null,
      club_id: null,
      player_id: null,
      page: "1",
    });
  };

  const activeFilters = [
    filters.seasonId && `Season: ${filters.seasonId}`,
    filters.clubId && `Club: ${filters.clubId}`,
    filters.playerId && `Player: ${filters.playerId}`,
  ].filter(Boolean);

  const heroSummary = (
    <Stack direction="row" spacing={1} flexWrap="wrap">
      {activeFilters.length === 0 ? (
        <Chip
          label="Filters: none"
          size="small"
          sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
        />
      ) : (
        activeFilters.map((item) => (
          <Chip
            key={item}
            label={item}
            size="small"
            sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
          />
        ))
      )}
    </Stack>
  );

  const hero = (
    <HeroBar
      title="Transfer History"
      subtitle="Audit completed transfers across seasons"
      tone="blue"
      kpis={[
        { label: "Records", value: pageMeta.count || "-", icon: <HistoryEduIcon fontSize="small" /> },
        { label: "Page", value: `${pageMeta.page}/${Math.max(pageMeta.totalPages, 1)}`, icon: <TimelineIcon fontSize="small" /> },
        { label: "Status", value: loading ? "Loading" : error ? "Error" : "Ready", icon: <QueryStatsIcon fontSize="small" /> },
        { label: "Filters", value: activeFilters.length || "0", icon: <FilterAltIcon fontSize="small" />, hint: activeFilters.join(" · ") || "None" },
      ]}
      actions={
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button component={RouterLink} to="/transfers" variant="outlined">
            Market
          </Button>
          <Button component={RouterLink} to="/transfers/my" variant="contained">
            My Deals
          </Button>
        </Stack>
      }
    />
  );

  const topSection = (
    <Stack spacing={3}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h2">
            Review completed deals
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Filter by season, club or player to inspect the transfer market trends across your universe.
          </Typography>
          <Stack spacing={1.5} mt={2}>
            <Typography variant="subtitle2">Filters overview</Typography>
            {heroSummary}
          </Stack>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <HistoryFilters
            value={filters}
            onChange={setFilters}
            onApply={handleApplyFilters}
            onClear={handleClearFilters}
            loading={loading}
          />
        </CardContent>
      </Card>
    </Stack>
  );

  const mainContent: ReactNode = (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
          <Typography variant="h5" component="h2">
            Completed Deals
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total: {pageMeta.count}
          </Typography>
        </Stack>

        <HistoryTable
          entries={records}
          loading={loading}
          pageMeta={pageMeta}
          onChangePage={(newPage) => updateSearchParams({ page: String(newPage) })}
        />
      </CardContent>
    </Card>
  );

  const asideContent: ReactNode = (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Active filters
        </Typography>
        {activeFilters.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            Showing all records.
          </Typography>
        ) : (
          <Stack spacing={0.5}>
            {activeFilters.map((item) => (
              <Typography key={item} variant="body2">
                {item}
              </Typography>
            ))}
          </Stack>
        )}
      </CardContent>
    </Card>
  );

  return <PageShell hero={hero} top={topSection} main={mainContent} aside={asideContent} />;
}

