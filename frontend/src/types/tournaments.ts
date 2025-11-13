export type ChampionshipStatus = "pending" | "in_progress" | "finished";

export interface SeasonSummary {
  id: number;
  name: string;
  number: number;
  is_active: boolean;
  start_date: string;
  end_date: string;
}

export interface LeagueSummary {
  id: number;
  name: string;
  country: string;
  level: number;
  max_teams: number;
}

export interface ChampionshipSummary {
  id: number;
  name: string;
  status: ChampionshipStatus;
  start_date: string;
  end_date: string;
  match_time?: string;
  season: SeasonSummary;
  league: LeagueSummary;
}

export interface ChampionshipTeamSummary {
  id: number;
  name: string;
  short_name?: string | null;
  crest_url?: string | null;
}

export interface ChampionshipStanding {
  team: ChampionshipTeamSummary;
  position: number;
  matches_played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_diff: number;
  points: number;
  is_relegation_zone?: boolean;
  is_promotion_zone?: boolean;
}

export interface ChampionshipMatchSummary {
  id: number;
  round: number;
  match_day: number;
  date: string;
  status: string;
  match_id: number;
  processed: boolean;
  home_team: ChampionshipTeamSummary;
  away_team: ChampionshipTeamSummary;
  score?: {
    home: number;
    away: number;
  } | null;
}

export interface ChampionshipDetailResponse {
  championship: ChampionshipSummary;
  standings: ChampionshipStanding[];
}

export interface ChampionshipMatchesResponse {
  matches: ChampionshipMatchSummary[];
}

export interface MyChampionshipResponse {
  championship: ChampionshipSummary;
  standings: ChampionshipStanding[];
  club_position: number;
  schedule: ChampionshipMatchSummary[];
}
