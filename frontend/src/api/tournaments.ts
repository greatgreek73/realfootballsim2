import {
  ChampionshipDetailResponse,
  ChampionshipMatchesResponse,
  ChampionshipSummary,
  LeagueSummary,
  MyChampionshipResponse,
  SeasonSummary,
} from "@/types/tournaments";

function resolveApiBase(): string {
  const explicit =
    typeof import.meta !== "undefined" &&
    (import.meta as any)?.env?.VITE_API_BASE &&
    String((import.meta as any).env.VITE_API_BASE);
  if (explicit) {
    return explicit;
  }

  return "";
}

const API_BASE = resolveApiBase();

function normalizeBase(base: string) {
  return base.endsWith("/") ? base.slice(0, -1) : base;
}

function buildUrl(path: string, query?: string) {
  const base = normalizeBase(API_BASE);
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const full = `${base}${normalizedPath}`;
  return query ? `${full}?${query}` : full;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(message?.detail ?? `HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

function buildQuery(params: Record<string, string | number | undefined | null>) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.append(key, String(value));
    }
  });
  return search.toString();
}

function withCredentials(input: RequestInfo | URL, init: RequestInit = {}) {
  return fetch(input, { credentials: "include", ...init });
}

export async function fetchChampionships(params: Record<string, string | number> = {}) {
  const query = buildQuery(params);
  const response = await withCredentials(
    buildUrl("/tournaments/api/championships", query),
  );
  return handleResponse<ChampionshipSummary[]>(response);
}

export async function fetchChampionshipDetail(championshipId: number) {
  const response = await withCredentials(
    buildUrl(`/tournaments/api/championships/${championshipId}/`),
  );
  return handleResponse<ChampionshipDetailResponse>(response);
}

export async function fetchChampionshipMatches(championshipId: number) {
  const response = await withCredentials(
    buildUrl(`/tournaments/api/championships/${championshipId}/matches/`),
  );
  return handleResponse<ChampionshipMatchesResponse>(response);
}

export async function fetchMyChampionship() {
  const response = await withCredentials(
    buildUrl(`/tournaments/api/championships/my/`),
  );
  return handleResponse<MyChampionshipResponse>(response);
}

export async function fetchSeasons() {
  const response = await withCredentials(buildUrl(`/tournaments/api/seasons/`));
  return handleResponse<SeasonSummary[]>(response);
}

export async function fetchLeagues(params: Record<string, string | number> = {}) {
  const query = buildQuery(params);
  const response = await withCredentials(
    buildUrl(`/tournaments/api/leagues`, query),
  );
  return handleResponse<LeagueSummary[]>(response);
}
