import { Card, CardContent, CardHeader, Skeleton, Stack, Typography } from "@mui/material";

import type { MatchSummary } from "@/api/matches";

type ClubFormStripProps = {
  matches: MatchSummary[];
  clubId?: number;
  loading: boolean;
};

type ResultToken = "W" | "D" | "L";

function getResult(match: MatchSummary, clubId?: number): ResultToken {
  if (!clubId) {
    return "D";
  }
  const isHome = match.home.id === clubId;
  const myScore = isHome ? match.score.home : match.score.away;
  const oppScore = isHome ? match.score.away : match.score.home;
  if (myScore > oppScore) return "W";
  if (myScore < oppScore) return "L";
  return "D";
}

function summarize(matches: MatchSummary[], clubId?: number) {
  return matches.reduce(
    (acc, match) => {
      const result = getResult(match, clubId);
      if (result === "W") acc.wins += 1;
      if (result === "D") acc.draws += 1;
      if (result === "L") acc.losses += 1;

      if (clubId) {
        const isHome = match.home.id === clubId;
        acc.goalsFor += isHome ? match.score.home : match.score.away;
        acc.goalsAgainst += isHome ? match.score.away : match.score.home;
      }
      return acc;
    },
    { wins: 0, draws: 0, losses: 0, goalsFor: 0, goalsAgainst: 0 },
  );
}

const tokenStyles: Record<ResultToken, { label: string; color: "success" | "warning" | "error" }> = {
  W: { label: "W", color: "success" },
  D: { label: "D", color: "warning" },
  L: { label: "L", color: "error" },
};

export default function ClubFormStrip({ matches, clubId, loading }: ClubFormStripProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader title="Recent form" subheader="Last five official matches" />
        <CardContent>
          <Skeleton height={48} />
        </CardContent>
      </Card>
    );
  }

  if (matches.length === 0) {
    return (
      <Card>
        <CardHeader title="Recent form" subheader="Last five official matches" />
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            No processed matches yet.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const summary = summarize(matches, clubId);
  const tokens = matches.slice(0, 5).map((match) => getResult(match, clubId));

  return (
    <Card>
      <CardHeader title="Recent form" subheader="Last five official matches" />
      <CardContent>
        <Stack spacing={1.5}>
          <Stack direction="row" spacing={1}>
            {tokens.map((token, index) => (
              <Typography
                key={`${token}-${index}`}
                variant="subtitle1"
              sx={{
                  bgcolor: (theme) => theme.palette[tokenStyles[token].color].light,
                  px: 2,
                  py: 0.75,
                  borderRadius: 1,
                  fontWeight: 600,
                  color: "text.primary",
                }}
              >
                {tokenStyles[token].label}
              </Typography>
            ))}
          </Stack>
          <Typography variant="body2" color="text.secondary">
            Record: {summary.wins}-{summary.draws}-{summary.losses} · Goals {summary.goalsFor}:
            {summary.goalsAgainst}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
