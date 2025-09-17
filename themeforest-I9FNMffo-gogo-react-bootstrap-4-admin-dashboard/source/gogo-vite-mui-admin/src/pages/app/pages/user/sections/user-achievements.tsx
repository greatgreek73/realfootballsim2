import { Link } from "react-router-dom";

import { Box, Card, CardContent, Chip, Typography } from "@mui/material";

import NiLike from "@/icons/nexture/ni-like";
import NiShuffle from "@/icons/nexture/ni-shuffle";
import NiUsers from "@/icons/nexture/ni-users";

export default function UserAchievements() {
  return (
    <Card className="mb-5">
      <CardContent>
        <Typography variant="h5" component="h5" className="card-title">
          Stocks
        </Typography>

        <Box className="flex flex-col gap-5">
          <Box className="flex flex-row items-center gap-3">
            <Box className="bg-primary-light/10 flex h-9 w-9 flex-none items-center justify-center rounded-md">
              <NiUsers size={"medium"} className="text-primary" />
            </Box>
            <Box className="flex flex-1 flex-col gap-2">
              <Box className="flex flex-row items-center justify-between">
                <Link to="/#" className="link-text-primary link-underline-hover font-semibold">
                  Social Media
                </Link>
                <Chip label="x4" variant="filled" />
              </Box>
            </Box>
          </Box>

          <Box className="flex flex-row items-center gap-3">
            <Box className="bg-secondary-light/10 flex h-9 w-9 flex-none items-center justify-center rounded-md">
              <NiShuffle size={"medium"} className="text-secondary" />
            </Box>
            <Box className="flex flex-1 flex-col gap-2">
              <Box className="flex flex-row items-center justify-between">
                <Link to="/#" className="link-text-primary link-underline-hover font-semibold">
                  Innovation Architect
                </Link>
                <Chip label="x2" variant="filled" />
              </Box>
            </Box>
          </Box>

          <Box className="flex flex-row items-center gap-3">
            <Box className="bg-accent-1-light/10 flex h-9 w-9 flex-none items-center justify-center rounded-md">
              <NiLike size={"medium"} className="text-accent-1" />
            </Box>
            <Box className="flex flex-1 flex-col gap-2">
              <Box className="flex flex-row items-center justify-between">
                <Link to="/#" className="link-text-primary link-underline-hover font-semibold">
                  Social Butterfly
                </Link>
                <Chip label="x2" variant="filled" />
              </Box>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
