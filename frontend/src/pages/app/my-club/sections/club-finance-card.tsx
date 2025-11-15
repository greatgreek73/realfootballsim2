import { Card, CardContent, CardHeader, Skeleton, Stack, Typography } from "@mui/material";

type ClubFinanceCardProps = {
  loading: boolean;
  tokens?: number;
  funds?: number;
};

function formatNumber(value?: number) {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
}

export default function ClubFinanceCard({ loading, tokens, funds }: ClubFinanceCardProps) {
  return (
    <Card>
      <CardHeader title="Finance snapshot" subheader="Track key resources" />
      <CardContent>
        {loading ? (
          <Skeleton height={80} />
        ) : (
          <Stack spacing={1.5}>
            <Stack>
              <Typography variant="subtitle2" color="text.secondary">
                Transfer funds
              </Typography>
              <Typography variant="h5">{formatNumber(funds)}</Typography>
            </Stack>
            <Stack>
              <Typography variant="subtitle2" color="text.secondary">
                Club tokens
              </Typography>
              <Typography variant="h5">{formatNumber(tokens)}</Typography>
            </Stack>
            <Typography variant="caption" color="text.secondary">
              Wage budget utilisation and detailed financial charts will appear here soon.
            </Typography>
          </Stack>
        )}
      </CardContent>
    </Card>
  );
}

