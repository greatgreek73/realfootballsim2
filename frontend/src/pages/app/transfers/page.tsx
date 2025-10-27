import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { Alert, Box, Button, Card, CardContent, Stack, Typography } from "@mui/material";

import { fetchTransferListings } from "@/api/transfers";
import { ListingFilters, ListingFiltersState } from "@/components/transfers/ListingFilters";
import { ListingTable, ListingsPageMeta } from "@/components/transfers/ListingTable";
import type { TransferListingListParams, TransferListingSummary } from "@/types/transfers";

const DEFAULT_FILTERS: ListingFiltersState = {
  position: "",
  minAge: "",
  maxAge: "",
  minPrice: "",
  maxPrice: "",
  status: "active",
};

export default function TransfersMarketPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [filters, setFilters] = useState<ListingFiltersState>(() => ({
    ...DEFAULT_FILTERS,
    position: searchParams.get("position") ?? "",
    minAge: searchParams.get("min_age") ?? "",
    maxAge: searchParams.get("max_age") ?? "",
    minPrice: searchParams.get("min_price") ?? "",
    maxPrice: searchParams.get("max_price") ?? "",
    status: (searchParams.get("status") as ListingFiltersState["status"]) ?? "active",
  }));

  const [listings, setListings] = useState<TransferListingSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pageMeta, setPageMeta] = useState<ListingsPageMeta>({
    page: 1,
    totalPages: 1,
    count: 0,
    pageSize: 30,
  });

  const page = useMemo(() => {
    const parsed = parseInt(searchParams.get("page") ?? "1", 10);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
  }, [searchParams]);

  useEffect(() => {
    setFilters((prev) => ({
      ...prev,
      position: searchParams.get("position") ?? "",
      minAge: searchParams.get("min_age") ?? "",
      maxAge: searchParams.get("max_age") ?? "",
      minPrice: searchParams.get("min_price") ?? "",
      maxPrice: searchParams.get("max_price") ?? "",
      status: (searchParams.get("status") as ListingFiltersState["status"]) ?? "active",
    }));
  }, [searchParams]);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const params: TransferListingListParams = {
          page,
          ordering: (searchParams.get("ordering") as TransferListingListParams["ordering"]) ?? undefined,
          position: searchParams.get("position") || undefined,
          status: (searchParams.get("status") as TransferListingListParams["status"]) ?? undefined,
        };

        const minAge = searchParams.get("min_age");
        const maxAge = searchParams.get("max_age");
        const minPrice = searchParams.get("min_price");
        const maxPrice = searchParams.get("max_price");

        if (minAge) params.minAge = Number(minAge);
        if (maxAge) params.maxAge = Number(maxAge);
        if (minPrice) params.minPrice = Number(minPrice);
        if (maxPrice) params.maxPrice = Number(maxPrice);

        const response = await fetchTransferListings(params);
        if (!controller.signal.aborted) {
          setListings(response.results);
          setPageMeta({
            page: response.page,
            totalPages: Math.max(response.total_pages, 1),
            count: response.count,
            pageSize: response.page_size,
          });
        }
      } catch (err: any) {
        if (!controller.signal.aborted) {
          setError(err?.message ?? "Не удалось загрузить список трансферов.");
          setListings([]);
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

  const DEFAULT_STATUS_PARAM = "active";

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
      position: filters.position || null,
      min_age: filters.minAge || null,
      max_age: filters.maxAge || null,
      min_price: filters.minPrice || null,
      max_price: filters.maxPrice || null,
      status: filters.status || DEFAULT_STATUS_PARAM,
      page: "1",
    });
  };

  const handleClearFilters = () => {
    setFilters(DEFAULT_FILTERS);
    updateSearchParams({
      position: null,
      min_age: null,
      max_age: null,
      min_price: null,
      max_price: null,
      status: DEFAULT_STATUS_PARAM,
      page: "1",
    });
  };

  return (
    <Box className="p-2 sm:p-4">
      <Stack direction={{ xs: "column", lg: "row" }} spacing={2} justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="h1" component="h1" className="mb-0">
            Transfer Market
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Browse active transfer listings, place bids, and monitor auction activity.
          </Typography>
        </Box>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button variant="outlined" onClick={handleClearFilters} disabled={loading}>
            Clear Filters
          </Button>
          <Button variant="contained" onClick={() => navigate("/transfers/create")}>
            List a Player
          </Button>
        </Stack>
      </Stack>

      {error && (
        <Alert severity="error" className="mt-3">
          {error}
        </Alert>
      )}

      <Card className="mt-3">
        <CardContent>
          <ListingFilters value={filters} onChange={setFilters} onApply={handleApplyFilters} onClear={handleClearFilters} loading={loading} />
        </CardContent>
      </Card>

      <Card className="mt-3">
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" className="mb-3">
            <Typography variant="h5" component="h2">
              Listings
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total: {pageMeta.count}
            </Typography>
          </Stack>

          <ListingTable
            listings={listings}
            loading={loading}
            pageMeta={pageMeta}
            onChangePage={(newPage) => updateSearchParams({ page: String(newPage) })}
            onView={(id) => navigate(`/transfers/${id}`)}
          />
        </CardContent>
      </Card>
    </Box>
  );
}
