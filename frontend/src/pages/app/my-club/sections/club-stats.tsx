import { Fragment } from "react";

import { Card, CardContent, Chip, Grid, Skeleton, Stack, Typography } from "@mui/material";

export type ClubStatsProps = {
  club: {
    tokens?: number;
    money?: number;
    status?: string;
  } | null;
  loading: boolean;
};

function formatNumber(value?: number): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "-";
  try {
    return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
  } catch (error) {
    return String(value);
  }
}

export default function ClubStats({ club, loading }: ClubStatsProps) {
  const cards = [
    {
      key: "tokens",
      label: "Tokens",
      value: club?.tokens,
      chipColor: "primary" as const,
    },
    {
      key: "money",
      label: "Money",
      value: club?.money,
      chipColor: "success" as const,
    },
    {
      key: "status",
      label: "Status",
      value: club?.status ?? "-",
      chipColor: "default" as const,
    },
  ];

  return (
    <Fragment>
      {cards.map((card) => (
        <Grid key={card.key} size={{ xs: 12, sm: 6, md: 4 }}>
          <Card className="h-full">
            <CardContent>
              <Stack spacing={1.5}>
                <Typography variant="subtitle2" color="text.secondary">
                  {card.label}
                </Typography>
                {loading ? (
                  <Skeleton height={36} />
                ) : (
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography variant="h4">
                      {card.key === "status" ? card.value : formatNumber(card.value as number | undefined)}
                    </Typography>
                    <Chip size="small" variant="outlined" color={card.chipColor} label={card.label} />
                  </Stack>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Fragment>
  );
}
