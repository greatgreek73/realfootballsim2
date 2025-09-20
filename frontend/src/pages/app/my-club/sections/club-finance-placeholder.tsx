import { Card, CardContent, Skeleton, Stack, Typography } from "@mui/material";

export type ClubFinancePlaceholderProps = {
  loading: boolean;
};

export default function ClubFinancePlaceholder({ loading }: ClubFinancePlaceholderProps) {
  return (
    <Card className="h-full">
      <CardContent className="flex h-full flex-col justify-between gap-2">
        <Stack spacing={1.5}>
          <Typography variant="h6">Finance &amp; Form</Typography>
          <Typography variant="body2" color="text.secondary">
            Track club finances and performance trends over time.
          </Typography>
        </Stack>
        {loading ? (
          <Stack spacing={1.5}>
            <Skeleton variant="rectangular" height={160} />
            <Skeleton height={20} width="60%" />
          </Stack>
        ) : (
          <Stack spacing={1}>
            <Typography variant="body2" color="text.secondary">
              Charts and analytics are coming soon.
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Once financial data is available, you will see income, expenses and form trends here.
            </Typography>
          </Stack>
        )}
      </CardContent>
    </Card>
  );
}
