import { getCsrfToken } from "@/lib/apiClient";

export type MatchStatus =
  | "scheduled"
  | "in_progress"
  | "paused"
  | "finished"
  | "cancelled"
  | "error";

export interface MatchTeamSummary {
  id: number;
  name: string;
  score: number;
}

export interface MatchCompetitionSummary {
  id: number;
  name: string | null;
  season: string | null;
  round: number | null;
  match_day: number | null;
}

export interface MatchSummary {
  id: number;
  datetime: string | null;
  status: MatchStatus;
  status_label: string;
  processed: boolean;
  home: MatchTeamSummary;
  away: MatchTeamSummary;
  score: {
    home: number;
    away: number;
  };
  competition: MatchCompetitionSummary | null;
}

export interface MatchListResponse {
  results: MatchSummary[];
  count: number;
  total_pages: number;
  page: number;
  page_size: number;
}

export interface MatchListParams {
  clubId?: number;
  status?: MatchStatus;
  processed?: boolean;
  page?: number;
  pageSize?: number;
  ordering?: "datetime" | "-datetime";
}

const DEFAULT_PARAMS: Required<Pick<MatchListParams, "page" | "pageSize" | "ordering">> = {
  page: 1,
  pageSize: 10,
  ordering: "-datetime",
};

export async function fetchMatches(params: MatchListParams = {}): Promise<MatchListResponse> {
  const search = new URLSearchParams();
  const merged = { ...DEFAULT_PARAMS, ...params };

  if (merged.clubId) search.set("club_id", String(merged.clubId));
  if (merged.status) search.set("status", merged.status);
  if (typeof merged.processed === "boolean") search.set("processed", merged.processed ? "true" : "false");
  if (merged.page && merged.page > 1) search.set("page", String(merged.page));
  if (merged.pageSize && merged.pageSize !== DEFAULT_PARAMS.pageSize) search.set("page_size", String(merged.pageSize));
  if (merged.ordering && merged.ordering !== DEFAULT_PARAMS.ordering) search.set("ordering", merged.ordering);

  const qs = search.toString();
  const res = await fetch(`/api/matches/${qs ? `?${qs}` : ""}`, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to fetch matches: ${res.status} ${res.statusText} - ${text}`);
  }
  return (await res.json()) as MatchListResponse;
}

export interface MatchTeamDetail extends MatchTeamSummary {
  tactic: string | null;
  lineup: unknown;
}

export interface MatchStats {
  shoots: number;
  passes: number;
  possessions: number;
  fouls: number;
  injuries: number;
  home_momentum: number;
  away_momentum: number;
  home_pass_streak: number;
  away_pass_streak: number;
}

export interface MatchDetail {
  id: number;
  status: MatchStatus;
  status_label: string;
  processed: boolean;
  datetime: string | null;
  started_at: string | null;
  last_minute_update: string | null;
  current_minute: number;
  waiting_for_next_minute: boolean;
  score: {
    home: number;
    away: number;
  };
  home: MatchTeamDetail;
  away: MatchTeamDetail;
  stats: MatchStats;
  competition: MatchCompetitionSummary | null;
}

export interface MatchEventPlayerSummary {
  id: number | null;
  name: string | null;
  position: string | null;
}

export interface MatchEvent {
  id: number;
  minute: number;
  type: string;
  type_label: string;
  description: string;
  personality_reason: string | null;
  timestamp: string | null;
  player: MatchEventPlayerSummary | null;
  related_player: MatchEventPlayerSummary | null;
}

export interface MatchEventsResponse {
  match: number;
  events: MatchEvent[];
}

export async function fetchMatchDetail(matchId: number): Promise<MatchDetail> {
  const res = await fetch(`/api/matches/${matchId}/`, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to load match ${matchId}: ${res.status} ${res.statusText} - ${text}`);
  }
  return (await res.json()) as MatchDetail;
}

export async function fetchMatchEvents(matchId: number): Promise<MatchEventsResponse> {
  const res = await fetch(`/api/matches/${matchId}/events/`, { credentials: "include" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to load match events ${matchId}: ${res.status} ${res.statusText} - ${text}`);
  }
  return (await res.json()) as MatchEventsResponse;
}

export interface CreateMatchPayload {
  homeTeamId?: number;
  awayTeamId?: number;
  datetime?: string;
  autoStart?: boolean;
  autoOpponent?: boolean;
}

export async function createMatch(payload: CreateMatchPayload = {}): Promise<MatchDetail> {
  const csrftoken = await getCsrfToken();
  const res = await fetch(`/api/matches/create/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    credentials: "include",
    body: JSON.stringify({
      home_team_id: payload.homeTeamId,
      away_team_id: payload.awayTeamId,
      datetime: payload.datetime,
      auto_start: payload.autoStart ?? true,
      auto_opponent: payload.autoOpponent ?? true,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to create match: ${res.status} ${res.statusText} - ${text}`);
  }
  const json = (await res.json()) as { match: MatchDetail };
  return json.match;
}

export interface SubstitutePlayerPayload {
  outPlayerId: number;
  inPlayerId?: number;
  description?: string;
}

export interface SubstitutePlayerResponse {
  match: MatchDetail;
  event: MatchEvent;
}

export async function substitutePlayer(matchId: number, payload: SubstitutePlayerPayload): Promise<SubstitutePlayerResponse> {
  const csrftoken = await getCsrfToken();
  const res = await fetch(`/api/matches/${matchId}/substitute/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    credentials: "include",
    body: JSON.stringify({
      out_player_id: payload.outPlayerId,
      in_player_id: payload.inPlayerId,
      description: payload.description,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to substitute player: ${res.status} ${res.statusText} - ${text}`);
  }
  return (await res.json()) as SubstitutePlayerResponse;
}
