import { ReactNode, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { Alert, Button, Card, CardContent, Chip, Stack, Typography } from "@mui/material";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import GavelIcon from "@mui/icons-material/Gavel";
import FilterAltIcon from "@mui/icons-material/FilterAlt";
import BarChartIcon from "@mui/icons-material/BarChart";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";
import { fetchTransferListings } from "@/api/transfers";
import { ListingFilters, ListingFiltersState } from "@/components/transfers/ListingFilters";
import { ListingTable, ListingsPageMeta } from "@/components/transfers/ListingTable";
import type { TransferListingListParams, TransferListingSummary } from "@/types/transfers";
import { resolveListingStatus } from "@/utils/transfers";

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
        const rawStatus = searchParams.get("status");
        const statusForRequest =
          rawStatus && rawStatus !== "expired"
            ? (rawStatus as TransferListingListParams["status"])
            : undefined;

        const params: TransferListingListParams = {
          page,
          ordering: (searchParams.get("ordering") as TransferListingListParams["ordering"]) ?? undefined,
          position: searchParams.get("position") || undefined,
          status: statusForRequest,
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
          const selectedStatus = searchParams.get("status");
          const filteredResults =
            selectedStatus && ["active", "completed", "cancelled", "expired"].includes(selectedStatus)
              ? response.results.filter(
                  (item) => resolveListingStatus(item.status, item.time_remaining) === selectedStatus
                )
              : response.results;

          if (import.meta.env.DEV) {
            console.debug(
              "[TransferMarket] listings snapshot",
              filteredResults.map((item) => ({
                id: item.id,
                status: item.status,
                effectiveStatus: resolveListingStatus(item.status, item.time_remaining),
                expires_at: item.expires_at,
                time_remaining: item.time_remaining,
              }))
            );
          }
          setListings(filteredResults);
          setPageMeta({
            page: response.page,
            totalPages: Math.max(response.total_pages, 1),
            count: selectedStatus ? filteredResults.length : response.count,
            pageSize: response.page_size,
          });
        }
      } catch (err: any) {
        if (!controller.signal.aborted) {
          setError(err?.message ?? "Failed to load transfer listings.");
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
      status: filters.status || null,
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

  const appliedFilters = [
    filters.status && `Status: ${filters.status}`,
    filters.position && `Position: ${filters.position}`,
    filters.minAge && `Min age: ${filters.minAge}`,
    filters.maxAge && `Max age: ${filters.maxAge}`,
    filters.minPrice && `Min price: ${filters.minPrice}`,
    filters.maxPrice && `Max price: ${filters.maxPrice}`,
  ].filter(Boolean);

  const hero = (
    <HeroBar
      title="Transfer Market"
      subtitle="Активные объявления клуба и глобальные аукционы"
      tone="orange"
      kpis={[
        { label: "Listings", value: pageMeta.count || "-", icon: <TrendingUpIcon fontSize="small" /> },
        {
          label: "Page",
          value: `${pageMeta.page}/${Math.max(pageMeta.totalPages, 1)}`,
          icon: <BarChartIcon fontSize="small" />,
        },
        {
          label: "Status",
          value: loading ? "Loading" : error ? "Error" : "Ready",
          icon: <GavelIcon fontSize="small" />,
        },
        {
          label: "Filter",
          value: filters.status || "all",
          icon: <FilterAltIcon fontSize="small" />,
        },
      ]}
      accent={
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {appliedFilters.length === 0 ? (
            <Chip
              label="Filters: none"
              size="small"
              sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
            />
          ) : (
            appliedFilters.map((item) => (
              <Chip
                key={item}
                label={item}
                size="small"
                sx={{ color: "white", borderColor: "white", bgcolor: "rgba(255,255,255,0.12)" }}
              />
            ))
          )}
        </Stack>
      }
      actions={
        <Button variant="contained" onClick={() => navigate("/transfers/create")}>
          List a Player
        </Button>
      }
    />
  );

  const topSection = (
    <Stack spacing={3}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h2">
            Browse active listings
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Use filters to narrow by position, age, price range or status, then open any row to inspect full details.
          </Typography>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <ListingFilters
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
  );

  const asideContent: ReactNode = (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Active filters
        </Typography>
        {appliedFilters.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No filters applied.
          </Typography>
        ) : (
          <Stack spacing={0.5}>
            {appliedFilters.map((item) => (
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
