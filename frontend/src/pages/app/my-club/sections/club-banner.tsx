import { ChangeEvent, useEffect, useMemo, useState } from "react";

import { Box, Button, Card, CardContent, Skeleton, Stack, Typography } from "@mui/material";
import type { CardProps } from "@mui/material";

export type ClubBannerProps = {
  club: {
    name?: string;
    country?: string;
    league?: string;
    status?: string;
  } | null;
  loading: boolean;
  badgeUrl?: string | null;
  onBadgeUpload?: (file: File) => void;
  onBadgeClear?: () => void;
  cardProps?: CardProps;
};

export default function ClubBanner({ club, loading, badgeUrl, onBadgeUpload, onBadgeClear, cardProps }: ClubBannerProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    setPreviewUrl(badgeUrl ?? null);
  }, [badgeUrl]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    onBadgeUpload?.(file);
    event.target.value = "";
  };

  const crestLetter = useMemo(() => (club?.name ? club.name.trim().charAt(0).toUpperCase() : "?"), [club?.name]);
  const crestDescription = previewUrl ? "Custom crest" : "Upload your crest";

  const nickname = "The Bulls";
  const foundedYear = "�᭮��� � 1924";
  const stadiumInfo = "�⠤��� Edgar Street, �����";
  const reputation = "�������: 78 / 100";

  return (
    <Card className="h-full" {...cardProps}>
      <CardContent
        className="flex h-full min-h-[220px] flex-col items-center justify-center gap-3 p-6"
        sx={{ flexGrow: 1 }}
      >
        {loading ? (
          <Stack spacing={2}>
            <Skeleton variant="text" height={32} width="60%" />
            <Skeleton variant="text" height={20} width="40%" />
            <Skeleton variant="text" height={20} width="30%" />
          </Stack>
        ) : club ? (
          <Stack direction={{ xs: "column", md: "row" }} spacing={3} alignItems="center" justifyContent="center">
            <Stack spacing={1.5} alignItems="center">
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
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Club crest"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  <Stack spacing={0.5} alignItems="center">
                    <Box
                      sx={{
                        width: 72,
                        height: 72,
                        borderRadius: "50%",
                        bgcolor: "grey.100",
                        color: "text.secondary",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontWeight: 700,
                        fontSize: 28,
                        boxShadow: 1,
                      }}
                    >
                      {crestLetter}
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {crestDescription}
                    </Typography>
                  </Stack>
                )}
              </Box>
              <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                <Button component="label" variant="outlined" size="small">
                  Upload crest
                  <input type="file" accept="image/*" hidden onChange={handleFileChange} />
                </Button>
                {previewUrl && (
                  <Button variant="text" color="secondary" size="small" onClick={onBadgeClear}>
                    Remove
                  </Button>
                )}
              </Stack>
            </Stack>
            <Stack spacing={2} flex={1} alignItems="center">
              <Typography variant="h3" component="h2" align="center">
                {club.name ?? "My Club"}
              </Typography>
              <Typography variant="h6" color="text.secondary" align="center">
                {nickname}
              </Typography>
              <Typography variant="body1" color="text.secondary" align="center">
                {foundedYear}
              </Typography>
              <Typography variant="body1" color="text.secondary" align="center">
                {stadiumInfo}
              </Typography>
              <Typography variant="body1" color="text.secondary" align="center">
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
