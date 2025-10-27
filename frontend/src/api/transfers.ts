import { getCsrfToken } from "@/lib/apiClient";
import {
  TransferHistoryListResponse,
  TransferHistoryParams,
  TransferListingActionResponse,
  TransferListingCreatePayload,
  TransferListingCreateResponse,
  TransferListingDetail,
  TransferListingListParams,
  TransferListingListResponse,
  TransferOfferActionResponse,
  TransferOfferCreatePayload,
} from "@/types/transfers";

const DEFAULT_LIST_PARAMS: Required<Pick<TransferListingListParams, "page" | "pageSize" | "ordering">> = {
  page: 1,
  pageSize: 30,
  ordering: "expires_at",
};

const DEFAULT_HISTORY_PARAMS: Required<Pick<TransferHistoryParams, "page" | "pageSize" | "ordering">> = {
  page: 1,
  pageSize: 20,
  ordering: "-transfer_date",
};

function buildListingsQuery(params: TransferListingListParams = {}): string {
  const search = new URLSearchParams();
  const merged = { ...DEFAULT_LIST_PARAMS, ...params };

  if (merged.page && merged.page > 1) search.set("page", String(merged.page));
  if (merged.pageSize && merged.pageSize !== DEFAULT_LIST_PARAMS.pageSize) {
    search.set("page_size", String(merged.pageSize));
  }
  if (merged.ordering && merged.ordering !== DEFAULT_LIST_PARAMS.ordering) {
    search.set("ordering", merged.ordering);
  }
  if (merged.position) search.set("position", merged.position);
  if (typeof merged.minAge === "number") search.set("min_age", String(merged.minAge));
  if (typeof merged.maxAge === "number") search.set("max_age", String(merged.maxAge));
  if (typeof merged.minPrice === "number") search.set("min_price", String(merged.minPrice));
  if (typeof merged.maxPrice === "number") search.set("max_price", String(merged.maxPrice));
  if (typeof merged.clubId === "number") search.set("club_id", String(merged.clubId));
  if (merged.status) search.set("status", merged.status);

  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

function buildHistoryQuery(params: TransferHistoryParams = {}): string {
  const search = new URLSearchParams();
  const merged = { ...DEFAULT_HISTORY_PARAMS, ...params };

  if (merged.page && merged.page > 1) search.set("page", String(merged.page));
  if (merged.pageSize && merged.pageSize !== DEFAULT_HISTORY_PARAMS.pageSize) {
    search.set("page_size", String(merged.pageSize));
  }
  if (merged.ordering && merged.ordering !== DEFAULT_HISTORY_PARAMS.ordering) {
    search.set("ordering", merged.ordering);
  }
  if (typeof merged.seasonId === "number") search.set("season_id", String(merged.seasonId));
  if (typeof merged.clubId === "number") search.set("club_id", String(merged.clubId));
  if (typeof merged.playerId === "number") search.set("player_id", String(merged.playerId));

  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

async function fetchJson<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const res = await fetch(input, init);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(
      `Transfer API request failed: ${res.status} ${res.statusText}${text ? ` - ${text}` : ""}`,
    );
  }
  if (res.status === 204) {
    return {} as T;
  }
  return (await res.json()) as T;
}

async function postJson<T>(url: string, payload?: unknown): Promise<T> {
  const csrftoken = await getCsrfToken();
  return fetchJson<T>(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    credentials: "include",
    body: payload ? JSON.stringify(payload) : "{}",
  });
}

export async function fetchTransferListings(
  params: TransferListingListParams = {},
): Promise<TransferListingListResponse> {
  const query = buildListingsQuery(params);
  return fetchJson<TransferListingListResponse>(`/api/transfers/listings/${query}`, {
    credentials: "include",
  });
}

export async function fetchTransferListing(listingId: number): Promise<TransferListingDetail> {
  return fetchJson<TransferListingDetail>(`/api/transfers/listings/${listingId}/`, {
    credentials: "include",
  });
}

export async function createTransferListing(
  payload: TransferListingCreatePayload,
): Promise<TransferListingCreateResponse> {
  return postJson<TransferListingCreateResponse>("/api/transfers/listings/", payload);
}

export async function cancelTransferListing(
  listingId: number,
): Promise<TransferListingActionResponse> {
  return postJson<TransferListingActionResponse>(`/api/transfers/listings/${listingId}/cancel/`);
}

export async function expireTransferListing(
  listingId: number,
): Promise<TransferListingActionResponse> {
  return postJson<TransferListingActionResponse>(`/api/transfers/listings/${listingId}/expire/`);
}

export async function createTransferOffer(
  listingId: number,
  payload: TransferOfferCreatePayload,
): Promise<TransferOfferActionResponse> {
  return postJson<TransferOfferActionResponse>(
    `/api/transfers/listings/${listingId}/offers/`,
    payload,
  );
}

export async function cancelTransferOffer(offerId: number): Promise<TransferOfferActionResponse> {
  return postJson<TransferOfferActionResponse>(`/api/transfers/offers/${offerId}/cancel/`);
}

export async function rejectTransferOffer(offerId: number): Promise<TransferOfferActionResponse> {
  return postJson<TransferOfferActionResponse>(`/api/transfers/offers/${offerId}/reject/`);
}

export async function acceptTransferOffer(offerId: number): Promise<TransferOfferActionResponse> {
  return postJson<TransferOfferActionResponse>(`/api/transfers/offers/${offerId}/accept/`);
}

export async function fetchTransferHistory(
  params: TransferHistoryParams = {},
): Promise<TransferHistoryListResponse> {
  const query = buildHistoryQuery(params);
  return fetchJson<TransferHistoryListResponse>(`/api/transfers/history/${query}`, {
    credentials: "include",
  });
}
