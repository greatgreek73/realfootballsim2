import { Card, CardContent, Skeleton, Stack, Typography } from "@mui/material";

export type ClubBannerProps = {
  club: {
    name?: string;
    country?: string;
    league?: string;
    status?: string;
  } | null;
  loading: boolean;
};

export default function ClubBanner({ club, loading }: ClubBannerProps) {
  return (
    <Card className="h-full">
      <CardContent className="flex h-full flex-col justify-between gap-3 p-6">
        {loading ? (
          <Stack spacing={2}>
            <Skeleton variant="text" height={32} width="60%" />
            <Skeleton variant="text" height={20} width="40%" />
            <Skeleton variant="text" height={20} width="30%" />
          </Stack>
        ) : club ? (
          <Stack spacing={1.5}>
            <Typography variant="h3" component="h2">
              {club.name ?? "My Club"}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {[club.country, club.league].filter(Boolean).join(" • ") || ""}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {club.status || "Status unknown"}
            </Typography>
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No club data available.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
