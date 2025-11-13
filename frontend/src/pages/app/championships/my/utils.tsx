import { type ReactNode } from "react";

import type { ChampionshipMatchSummary, ChampionshipStanding } from "@/types/tournaments";

export type FixtureDifficultyMetric = {
  value: string;
  hint: ReactNode;
  badge: {
    label: string;
    tone: "success" | "caution" | "warning" | "danger";
  };
  tooltip: string;
  matchCount: number;
};

export type GapMetric = {
  value: string;
  hint: ReactNode;
  badge: {
    label: string;
    tone: "success" | "warning" | "danger";
  };
  tooltip: string;
};

export type RoundGroup = {
  round: number;
  matches: ChampionshipMatchSummary[];
  dateRange: string;
};

export function formatDateTime(dateString: string): string {
  return new Intl.DateTimeFormat(undefined, {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateString));
}

export function formatRoundRange(startISO: string, endISO: string): string {
  if (!startISO) {
    return "TBD";
  }
  const start = new Date(startISO);
  const end = endISO ? new Date(endISO) : start;
  const sameDay = start.toDateString() === end.toDateString();

  const label = (date: Date) =>
    new Intl.DateTimeFormat(undefined, {
      day: "2-digit",
      month: "2-digit",
    }).format(date);

  if (sameDay) {
    return label(start);
  }
  return `${label(start)}–${label(end)}`;
}

export function groupMatchesByRound(schedule: ChampionshipMatchSummary[]): RoundGroup[] {
  const map = new Map<number, ChampionshipMatchSummary[]>();
  schedule.forEach((match) => {
    if (!map.has(match.round)) {
      map.set(match.round, []);
    }
    map.get(match.round)!.push(match);
  });

  return Array.from(map.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([round, matches]) => {
      const sorted = matches.slice().sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      const firstDate = sorted[0]?.date ?? "";
      const lastDate = sorted[sorted.length - 1]?.date ?? firstDate;
      return {
        round,
        matches: sorted,
        dateRange: formatRoundRange(firstDate, lastDate),
      };
    });
}

export function describeMatchStatus(match: ChampionshipMatchSummary): string {
  if (match.status === "finished" && match.score) {
    return `Finished ${match.score.home}:${match.score.away}`;
  }
  if (match.status === "in_progress") {
    return "Live";
  }
  if (match.status === "scheduled") {
    return formatDateTime(match.date);
  }
  return match.status.replace("_", " ");
}

export function determineCurrentRound(schedule: ChampionshipMatchSummary[], now: number): number | null {
  if (schedule.length === 0) {
    return null;
  }

  const pastOrLive = schedule.filter(
    (match) => new Date(match.date).getTime() <= now || match.status === "in_progress",
  );
  if (pastOrLive.length === 0) {
    return schedule[0].round;
  }
  return pastOrLive[pastOrLive.length - 1]?.round ?? null;
}

export function isUpcomingMatch(match: ChampionshipMatchSummary, now: number): boolean {
  if (match.status === "finished") {
    return new Date(match.date).getTime() >= now;
  }
  return true;
}

export function getResultBadge(
  match: ChampionshipMatchSummary,
  clubId?: number | null,
): { label: string; tone: "success" | "error" | "warning" | "info" | "default" } {
  if (!clubId || match.status !== "finished" || !match.score) {
    if (match.status === "in_progress") {
      return { label: "Live", tone: "warning" };
    }
    if (match.status === "scheduled") {
      return { label: formatDateTime(match.date), tone: "info" };
    }
    return { label: describeMatchStatus(match), tone: "default" };
  }

  const isHome = match.home_team.id === clubId;
  const goalsFor = isHome ? match.score.home : match.score.away;
  const goalsAgainst = isHome ? match.score.away : match.score.home;
  const label = `${match.score.home}:${match.score.away}`;

  if (goalsFor > goalsAgainst) {
    return { label: `W ${label}`, tone: "success" };
  }
  if (goalsFor < goalsAgainst) {
    return { label: `L ${label}`, tone: "error" };
  }
  return { label: `D ${label}`, tone: "warning" };
}

export function buildFixtureDifficulty({
  schedule,
  standings,
  clubPosition,
  clubTeamId,
}: {
  schedule: ChampionshipMatchSummary[];
  standings: ChampionshipStanding[];
  clubPosition?: number | null;
  clubTeamId?: number | null;
}): FixtureDifficultyMetric | null {
  if (!Array.isArray(schedule) || schedule.length === 0) {
    return null;
  }

  const clubId =
    clubTeamId ??
    standings.find((row) => row.position === clubPosition)?.team.id ??
    null;
  if (!clubId) {
    return null;
  }

  const now = Date.now();
  const upcoming = schedule
    .filter((match) => {
      const matchTime = new Date(match.date).getTime();
      const involvesClub = match.home_team.id === clubId || match.away_team.id === clubId;
      return involvesClub && matchTime >= now;
    })
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 3);

  if (upcoming.length === 0) {
    return null;
  }

  const positionMap = new Map(standings.map((row) => [row.team.id, row.position]));
  const totalTeams =
    standings.length > 0
      ? standings.length
      : Math.max(
          ...schedule
            .map((match) => [match.home_team.id, match.away_team.id])
            .flat()
            .map((teamId) => positionMap.get(teamId) ?? 0),
          1,
        );

  const processed = upcoming.map((match) => {
    const isHome = match.home_team.id === clubId;
    const opponentId = isHome ? match.away_team.id : match.home_team.id;
    const opponentPosition = positionMap.get(opponentId);
    const baseDifficulty =
      opponentPosition && totalTeams > 1 ? positionToDifficulty(opponentPosition, totalTeams) : 3;
    const travelAdjustment = isHome ? -0.2 : 0.3;
    const adjusted = baseDifficulty + travelAdjustment;
    const positionLabel = opponentPosition ?? "?";
    return {
      adjusted,
      isHome,
      positionLabel,
    };
  });

  const availableMatches = processed.length;
  if (availableMatches === 0) {
    return null;
  }

  const average = processed.reduce((sum, item) => sum + item.adjusted, 0) / availableMatches;
  const clamped = Math.min(5, Math.max(1, average));
  const rounded = Math.round(clamped * 2) / 2;
  const formattedScore = rounded.toFixed(1);

  let label: "Easy" | "Moderate" | "Hard" | "Very Hard";
  let tone: "success" | "caution" | "warning" | "danger";
  if (rounded >= 4.5) {
    label = "Very Hard";
    tone = "danger";
  } else if (rounded >= 3.5) {
    label = "Hard";
    tone = "warning";
  } else if (rounded >= 2.5) {
    label = "Moderate";
    tone = "caution";
  } else {
    label = "Easy";
    tone = "success";
  }

  const matchCountLabel = `Next ${availableMatches} match${availableMatches === 1 ? "" : "es"}`;
  const chips = processed.map((item, index) => (
    <span
      key={`${item.positionLabel}-${index}`}
      className="inline-flex items-center gap-1 rounded-full bg-white/20 px-2 py-0.5 text-[11px]"
      title={item.isHome ? "Home" : "Away"}
    >
      <span>{item.isHome ? "🏠" : "✈️"}</span>
      <span>{item.positionLabel}</span>
    </span>
  ));
  const hint = (
    <div className="flex flex-wrap items-center gap-2">
      <span>{matchCountLabel}</span>
      <span>·</span>
      <div className="flex flex-wrap gap-1" aria-label="Upcoming opponents (🏠 home / ✈️ away)">
        {chips}
      </div>
    </div>
  );

  return {
    value: `${formattedScore} / 5 - ${label}`,
    hint,
    badge: { label, tone },
    tooltip: `${matchCountLabel} difficulty (auto, legend: 🏠 home / ✈️ away)`,
    matchCount: availableMatches,
  };
}

export function buildGapToTarget({
  standings,
  clubPosition,
  leagueLevel,
}: {
  standings: ChampionshipStanding[];
  clubPosition?: number | null;
  leagueLevel: number;
}): GapMetric | null {
  if (!Array.isArray(standings) || standings.length === 0 || clubPosition == null) {
    return null;
  }

  const clubRow = standings.find((row) => row.position === clubPosition);
  if (!clubRow) {
    return null;
  }

  const totalTeams = standings.length;
  const relegatedRows = standings.filter((row) => row.is_relegation_zone);
  const firstRelegatedPos =
    relegatedRows.length > 0 ? Math.min(...relegatedRows.map((row) => row.position)) : totalTeams + 1;
  const lastSafePos = Math.min(totalTeams, Math.max(1, firstRelegatedPos - 1));
  const isBottomContext = clubRow.position >= lastSafePos;

  let targetRow: ChampionshipStanding | undefined;
  let targetCategory = "";

  if (clubRow.position <= 3) {
    const leaderRow = standings.find((row) => row.position === 1);
    const runnerUpRow = standings.find((row) => row.position === Math.min(2, totalTeams));
    const chasingLeader = clubRow.position !== 1;
    targetRow = chasingLeader ? leaderRow : runnerUpRow ?? leaderRow;
    targetCategory = chasingLeader ? "Leader" : "Runner-up";
  } else if (isBottomContext) {
    const firstRelegatedRow = standings.find((row) => row.position === firstRelegatedPos);
    const lastSafeRow = standings.find((row) => row.position === lastSafePos);
    targetRow = clubRow.position >= firstRelegatedPos ? lastSafeRow ?? firstRelegatedRow : firstRelegatedRow ?? lastSafeRow;
    targetCategory = "Safety";
  } else {
    const playoffCutoff = Math.min(leagueLevel === 1 ? 4 : 6, totalTeams);
    const cutoffRow = standings.find((row) => row.position === playoffCutoff);
    const outsideRow = standings.find((row) => row.position === Math.min(playoffCutoff + 1, totalTeams));
    targetRow = clubRow.position <= playoffCutoff ? outsideRow ?? cutoffRow : cutoffRow ?? outsideRow;
    targetCategory = `Top-${playoffCutoff}`;
  }

  if (!targetRow || !targetCategory) {
    return null;
  }

  const rawGap = targetRow.points - clubRow.points;
  const neededGap = Math.max(0, rawGap);
  const absGap = Math.abs(rawGap);
  const badge =
    neededGap <= 2
      ? { label: "Close", tone: "success" as const }
      : neededGap <= 5
      ? { label: "Chase", tone: "warning" as const }
      : { label: "Tough", tone: "danger" as const };

  const value =
    rawGap === 0
      ? `Level with ${targetCategory}`
      : rawGap > 0
      ? `${absGap} pts off ${targetCategory}`
      : `${absGap} pts clear ${targetCategory}`;

  const hint = (
    <span>
      You: {clubRow.points} pts (MP {clubRow.matches_played})
    </span>
  );

  return {
    value,
    hint,
    badge,
    tooltip: `Target = ${targetCategory} (auto). Click to change target.`,
  };
}

export function formatOrdinal(position: number): string {
  const suffixes: Record<number, string> = { 1: "st", 2: "nd", 3: "rd" };
  const remainder = position % 100;
  if (remainder >= 11 && remainder <= 13) {
    return `${position}th`;
  }
  return `${position}${suffixes[position % 10] ?? "th"}`;
}

function positionToDifficulty(position: number, totalTeams: number): number {
  if (totalTeams <= 1) {
    return 3;
  }
  const normalized = 1 - (position - 1) / (totalTeams - 1);
  return 1 + normalized * 4;
}
