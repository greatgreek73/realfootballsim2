import { Box, Card, CardContent, Grid, Typography } from "@mui/material";

import NiBasket from "@/icons/nexture/ni-basket";
import NiCatalog from "@/icons/nexture/ni-catalog";
import NiCells from "@/icons/nexture/ni-cells";
import NiPercent from "@/icons/nexture/ni-percent";
import NiQuestionHexagon from "@/icons/nexture/ni-question-hexagon";
import NiScreen from "@/icons/nexture/ni-screen";
import NiStars from "@/icons/nexture/ni-stars";
import NiUser from "@/icons/nexture/ni-user";

export default function DashboardAnalyticsStats() {
  return (
    <>
      <Grid size={{ xs: 6, sm: 3 }}>
        <Card component="a" href="#" className="flex flex-col p-1 transition-transform hover:scale-[1.02]">
          <Box className="bg-primary-light/10 flex h-[4.5rem] w-full flex-none items-center justify-center rounded-2xl">
            <NiBasket className="text-primary" size={"large"} />
          </Box>
          <CardContent className="text-center">
            <Typography variant="body1" className="text-text-secondary leading-5 transition-colors">
              Orders
            </Typography>
            <Typography variant="h5" className="text-leading-5">
              182
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 6, sm: 3 }}>
        <Card component="a" href="#" className="flex flex-col p-1 transition-transform hover:scale-[1.02]">
          <Box className="bg-secondary-light/10 flex h-[4.5rem] w-full flex-none items-center justify-center rounded-2xl">
            <NiCells className="text-secondary" size={"large"} />
          </Box>
          <CardContent className="text-center">
            <Typography variant="body1" className="text-text-secondary leading-5 transition-colors">
              Products
            </Typography>
            <Typography variant="h5" className="text-leading-5">
              264
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 6, sm: 3 }}>
        <Card component="a" href="#" className="flex flex-col p-1 transition-transform hover:scale-[1.02]">
          <Box className="bg-primary-light/10 flex h-[4.5rem] w-full flex-none items-center justify-center rounded-2xl">
            <NiCatalog className="text-primary" size={"large"} />
          </Box>
          <CardContent className="text-center">
            <Typography variant="body1" className="text-text-secondary leading-5 transition-colors">
              Categories
            </Typography>
            <Typography variant="h5" className="text-leading-5">
              42
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 6, sm: 3 }}>
        <Card component="a" href="#" className="flex flex-col p-1 transition-transform hover:scale-[1.02]">
          <Box className="bg-secondary-light/10 flex h-[4.5rem] w-full flex-none items-center justify-center rounded-2xl">
            <NiUser className="text-secondary" size={"large"} />
          </Box>
          <CardContent className="text-center">
            <Typography variant="body1" className="text-text-secondary leading-5 transition-colors">
              Users
            </Typography>
            <Typography variant="h5" className="text-leading-5">
              1,487
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 6, sm: 3 }}>
        <Card component="a" href="#" className="flex flex-col p-1 transition-transform hover:scale-[1.02]">
          <Box className="bg-primary-light/10 flex h-[4.5rem] w-full flex-none items-center justify-center rounded-2xl">
            <NiStars className="text-primary" size={"large"} />
          </Box>
          <CardContent className="text-center">
            <Typography variant="body1" className="text-text-secondary leading-5 transition-colors">
              Reviews
            </Typography>
            <Typography variant="h5" className="text-leading-5">
              124
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 6, sm: 3 }}>
        <Card component="a" href="#" className="flex flex-col p-1 transition-transform hover:scale-[1.02]">
          <Box className="bg-secondary-light/10 flex h-[4.5rem] w-full flex-none items-center justify-center rounded-2xl">
            <NiScreen className="text-secondary" size={"large"} />
          </Box>
          <CardContent className="text-center">
            <Typography variant="body1" className="text-text-secondary leading-5 transition-colors">
              Visits
            </Typography>
            <Typography variant="h5" className="text-leading-5">
              48,745
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 6, sm: 3 }}>
        <Card component="a" href="#" className="flex flex-col p-1 transition-transform hover:scale-[1.02]">
          <Box className="bg-primary-light/10 flex h-[4.5rem] w-full flex-none items-center justify-center rounded-2xl">
            <NiQuestionHexagon className="text-primary" size={"large"} />
          </Box>
          <CardContent className="text-center">
            <Typography variant="body1" className="text-text-secondary leading-5 transition-colors">
              Questions
            </Typography>
            <Typography variant="h5" className="text-leading-5">
              45
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 6, sm: 3 }}>
        <Card component="a" href="#" className="flex flex-col p-1 transition-transform hover:scale-[1.02]">
          <Box className="bg-secondary-light/10 flex h-[4.5rem] w-full flex-none items-center justify-center rounded-2xl">
            <NiPercent className="text-secondary" size={"large"} />
          </Box>
          <CardContent className="text-center">
            <Typography variant="body1" className="text-text-secondary leading-5 transition-colors">
              Discounts
            </Typography>
            <Typography variant="h5" className="text-leading-5">
              4
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </>
  );
}
