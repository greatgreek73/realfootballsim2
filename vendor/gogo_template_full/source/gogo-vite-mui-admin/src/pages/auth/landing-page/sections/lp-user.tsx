import { useState } from "react";
import { useTranslation } from "react-i18next";

import { Avatar, Box, Button, Card, CardContent, Link, Typography } from "@mui/material";

import NiBookmark from "@/icons/nexture/ni-bookmark";
import NiPin from "@/icons/nexture/ni-pin";
import { cn } from "@/lib/utils";

export default function LPUser() {
  const { t } = useTranslation();
  const [following, setFollowing] = useState(true);
  return (
    <Card className="w-[340px]">
      <CardContent className="flex flex-row gap-2.5">
        <Avatar
          alt="Laura Ellis"
          src="/images/avatars/avatar-1.jpg"
          className={cn("medium cursor-pointer transition-all", following ? "grayscale-0" : "grayscale-75")}
        />

        <Box className="flex flex-1 flex-col gap-4">
          <Box className="mb-1 flex flex-row items-start justify-between gap-1">
            <Box className="flex flex-col">
              <Link href="#" variant="subtitle2" underline="hover" color="textPrimary" className="-mb-1 pt-0.25">
                Laura Ellis
              </Link>
              <Typography className="text-text-secondary" variant="body1">
                {t("landing-frontend-developer")}
              </Typography>
            </Box>
            <Button
              variant="pastel"
              color={following ? "grey" : "primary"}
              size="tiny"
              onClick={() => {
                setFollowing(!following);
              }}
            >
              {following ? t("landing-following") : t("landing-follow")}
            </Button>
          </Box>

          <Box className="flex flex-col justify-between gap-2">
            <Box className="flex flex-row gap-2.5">
              <NiPin className="text-primary" />
              <Typography variant="body1">Cologne, Germany</Typography>
            </Box>
            <Box className="flex flex-row gap-2.5">
              <NiBookmark className="text-secondary" />
              <Typography variant="body1">University of Cologne</Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
