export type TransferListingStatus = "active" | "completed" | "cancelled" | "expired";

export type TransferOfferStatus = "pending" | "accepted" | "rejected" | "cancelled";

export interface TransferClubSummary {
  id: number;
  name: string;
  crest_url?: string | null;
  owner_id?: number | null;
}

export interface TransferPlayerSummary {
  id: number;
  full_name: string;
  position: string;
  age: number;
  overall_rating: number;
  nationality?: string | null;
  club_id?: number | null;
}

export interface TransferListingSummaryInfo {
  offers_count: number;
  is_owner: boolean;
  can_bid: boolean;
}

export interface TransferListingSummary {
  id: number;
  status: TransferListingStatus;
  asking_price: number;
  highest_bid: number | null;
  listed_at: string;
  expires_at: string | null;
  time_remaining: number | null;
  player: TransferPlayerSummary;
  club: TransferClubSummary;
  summary: TransferListingSummaryInfo;
}

export interface TransferListingExtendedInfo extends TransferListingSummary {
  description?: string | null;
  duration?: number | null;
}

export interface TransferListingPermissions {
  is_owner: boolean;
  can_bid: boolean;
  can_cancel_listing: boolean;
  can_accept_offers: boolean;
}

export interface TransferOfferSummary {
  id: number;
  bid_amount: number;
  status: TransferOfferStatus;
  created_at: string;
  bidding_club: TransferClubSummary;
  is_own_offer?: boolean;
  is_highest?: boolean;
  can_cancel?: boolean;
  can_accept?: boolean;
  can_reject?: boolean;
  message?: string | null;
}

export interface TransferListingDetail {
  listing: TransferListingExtendedInfo;
  offers: TransferOfferSummary[];
  permissions: TransferListingPermissions;
  [key: string]: unknown;
}

export interface TransferListingListResponse {
  results: TransferListingSummary[];
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TransferListingListParams {
  page?: number;
  pageSize?: number;
  ordering?: "expires_at" | "-expires_at" | "asking_price" | "-asking_price";
  position?: string;
  minAge?: number;
  maxAge?: number;
  minPrice?: number;
  maxPrice?: number;
  clubId?: number;
  status?: TransferListingStatus;
}

export interface TransferListingCreatePayload {
  player_id: number;
  asking_price: number;
  duration?: number;
  description?: string | null;
}

export interface TransferListingCreateResponse extends TransferListingDetail {}

export interface TransferListingActionResponse extends TransferListingDetail {}

export interface TransferOfferCreatePayload {
  bid_amount: number;
  message?: string | null;
}

export interface TransferOfferActionResponse extends TransferListingDetail {}

export interface TransferHistoryClubSummary {
  id: number;
  name: string;
}

export interface TransferHistoryEntry {
  id: number;
  player: TransferPlayerSummary;
  from_club: TransferHistoryClubSummary | null;
  to_club: TransferHistoryClubSummary | null;
  transfer_fee: number;
  transfer_date: string;
  season: {
    id: number;
    name: string;
  } | null;
}

export interface TransferHistoryListResponse {
  results: TransferHistoryEntry[];
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TransferHistoryParams {
  page?: number;
  pageSize?: number;
  ordering?: "-transfer_date" | "transfer_date";
  seasonId?: number;
  clubId?: number;
  playerId?: number;
}
