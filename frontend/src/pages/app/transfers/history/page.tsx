import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { Alert, Box, Button, Card, CardContent, Stack, Typography } from "@mui/material";

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
          setError(err?.message ?? "Не удалось загрузить историю трансферов.");
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

  return (
    <Box className="p-2 sm:p-4">
      <Stack direction={{ xs: "column", md: "row" }} spacing={2} justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="h1" component="h1" className="mb-0">
            История трансферов
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Просматривайте завершённые переходы и фильтруйте их по сезону, клубу и игроку.
          </Typography>
        </Box>
        <Button variant="outlined" onClick={handleClearFilters} disabled={loading}>
          Сбросить фильтры
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" className="mt-3">
          {error}
        </Alert>
      )}

      <Card className="mt-3">
        <CardContent>
          <HistoryFilters value={filters} onChange={setFilters} onApply={handleApplyFilters} onClear={handleClearFilters} loading={loading} />
        </CardContent>
      </Card>

      <Card className="mt-3">
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
            <Typography variant="h5" component="h2">
              Завершённые сделки
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Всего: {pageMeta.count}
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
    </Box>
  );
}
