import { Link as RouterLink } from "react-router-dom";

import {
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Chip,
  Skeleton,
  Stack,
  Typography,
} from "@mui/material";

import type { MatchSummary } from "@/api/matches";

type ClubRecentResultsProps = {
  matches: MatchSummary[];
  clubId?: number;
  loading: boolean;
};

type ResultToken = "W" | "D" | "L";

function getResult(match: MatchSummary, clubId?: number): ResultToken {
  if (!clubId) return "D";
  const isHome = match.home.id === clubId;
  const myScore = isHome ? match.score.home : match.score.away;
  const oppScore = isHome ? match.score.away : match.score.home;
  if (myScore > oppScore) return "W";
  if (myScore < oppScore) return "L";
  return "D";
}

const chipColor: Record<ResultToken, "success" | "warning" | "error"> = {
  W: "success",
  D: "warning",
  L: "error",
};

function formatDate(value: string | null) {
  if (!value) return "TBD";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "2-digit",
  }).format(date);
}

export default function ClubRecentResults({ matches, clubId, loading }: ClubRecentResultsProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader title="Recent results" subheader="Last three official matches" />
        <CardContent>
          <Skeleton height={64} />
          <Skeleton height={64} />
          <Skeleton height={64} />
        </CardContent>
      </Card>
    );
  }

  if (!matches.length) {
    return (
      <Card>
        <CardHeader title="Recent results" subheader="Last three official matches" />
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            No results recorded yet.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader title="Recent results" subheader="Last three official matches" />
      <CardContent>
        <Stack spacing={2}>
          {matches.map((match) => {
            const isHome = clubId ? match.home.id === clubId : true;
            const opponent = isHome ? match.away.name : match.home.name;
            const result = getResult(match, clubId);
            const scoreline = `${match.score.home} : ${match.score.away}`;
            return (
              <Stack key={match.id} direction="row" justifyContent="space-between" spacing={2}>
                <Stack spacing={0.25}>
                  <Typography variant="body1">
                    {isHome ? "vs" : "@"} {opponent}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(match.datetime)} · {match.competition?.name ?? "League"}
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="subtitle1" fontWeight={600}>
                    {scoreline}
                  </Typography>
                  <Chip size="small" label={result} color={chipColor[result]} />
                </Stack>
              </Stack>
            );
          })}
        </Stack>
      </CardContent>
      <CardActions>
        <Button component={RouterLink} to="/matches/history" size="small">
          View all results
        </Button>
      </CardActions>
    </Card>
  );
}
