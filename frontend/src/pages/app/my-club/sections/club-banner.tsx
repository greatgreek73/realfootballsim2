import { Box, Card, CardContent, Skeleton, Stack, Typography } from "@mui/material";

import HerefordBadge from "@/assets/hereford-united.svg";

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
  const nickname = "The Bulls";
  const foundedYear = "Основан в 1924";
  const stadiumInfo = "Стадион Edgar Street, Херефорд";
  const reputation = "Репутация: 78 / 100";
  return (
    <Card className="h-full">
      <CardContent className="flex h-full min-h-[220px] flex-col justify-between gap-3 p-6">
        {loading ? (
          <Stack spacing={2}>
            <Skeleton variant="text" height={32} width="60%" />
            <Skeleton variant="text" height={20} width="40%" />
            <Skeleton variant="text" height={20} width="30%" />
          </Stack>
        ) : club ? (
          <Stack direction={{ xs: "column", md: "row" }} spacing={3} alignItems="center">
            <Box
              sx={{
                width: { xs: 160, md: 200 },
                height: { xs: 160, md: 200 },
                borderRadius: 4,
                overflow: "hidden",
                boxShadow: 4,
                bgcolor: "background.default",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <img
                src={HerefordBadge}
                alt="Club crest"
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            </Box>
            <Stack spacing={2} flex={1}>
              <Typography variant="h3" component="h2">
                {club.name ?? "My Club"}
              </Typography>
              <Typography variant="h6" color="text.secondary">
                {nickname}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {foundedYear}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {stadiumInfo}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {reputation}
              </Typography>
            </Stack>
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
