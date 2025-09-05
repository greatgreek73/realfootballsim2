import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
  Typography,
} from "@mui/material";

import NiEmail from "@/template_full/icons/nexture/ni-email";
import NiLinkBroken from "@/template_full/icons/nexture/ni-link-broken";
import NiScreen from "@/template_full/icons/nexture/ni-screen";
import NiSearch from "@/template_full/icons/nexture/ni-search";
import NiTriangleDown from "@/template_full/icons/nexture/ni-triangle-down";
import NiTriangleUp from "@/template_full/icons/nexture/ni-triangle-up";
import NiWallet from "@/template_full/icons/nexture/ni-wallet";

export default function DashboardDefaultSources() {
  return (
    <Card className="h-full">
      <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
        Traffic Sources
      </Typography>
      <CardContent className="p-0! pb-2!">
        <List>
          <ListItem className="px-0 py-0">
            <ListItemButton classes={{ root: "group items-center justify-between" }}>
              <Box className="flex flex-row items-center">
                <ListItemAvatar>
                  <Avatar className="medium bg-primary-light/10 mr-3">
                    <NiSearch className="text-primary" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  className="w-40 flex-none"
                  primary={
                    <Typography component="p" variant="subtitle2" className="leading-4">
                      1. Organic Search
                    </Typography>
                  }
                />
              </Box>
              <Button
                className="pointer-events-none self-center"
                size="tiny"
                color="success"
                variant="pastel"
                startIcon={<NiTriangleUp size={"tiny"} />}
              >
                3.1%
              </Button>
              <Typography component="p">4,482</Typography>
            </ListItemButton>
          </ListItem>

          <ListItem className="px-0 py-0">
            <ListItemButton classes={{ root: "group items-center justify-between" }}>
              <Box className="flex flex-row items-center">
                <ListItemAvatar>
                  <Avatar className="medium bg-secondary-light/10 mr-3">
                    <NiScreen className="text-secondary" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  className="w-40 flex-none"
                  primary={
                    <Typography component="p" variant="subtitle2" className="leading-4">
                      2. Direct
                    </Typography>
                  }
                />
              </Box>
              <Button
                className="pointer-events-none self-center"
                size="tiny"
                color="success"
                variant="pastel"
                startIcon={<NiTriangleUp size={"tiny"} />}
              >
                2.7%
              </Button>
              <Typography component="p">3,672</Typography>
            </ListItemButton>
          </ListItem>

          <ListItem className="px-0 py-0">
            <ListItemButton classes={{ root: "group items-center justify-between" }}>
              <Box className="flex flex-row items-center">
                <ListItemAvatar>
                  <Avatar className="medium bg-accent-1-light/10 mr-3">
                    <NiLinkBroken className="text-accent-1" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  className="w-40 flex-none"
                  primary={
                    <Typography component="p" variant="subtitle2" className="leading-4">
                      3. Refferral
                    </Typography>
                  }
                />
              </Box>
              <Button
                className="pointer-events-none self-center"
                size="tiny"
                color="success"
                variant="pastel"
                startIcon={<NiTriangleUp size={"tiny"} />}
              >
                5.7%
              </Button>
              <Typography component="p">1,884</Typography>
            </ListItemButton>
          </ListItem>

          <ListItem className="px-0 py-0">
            <ListItemButton classes={{ root: "group items-center justify-between" }}>
              <Box className="flex flex-row items-center">
                <ListItemAvatar>
                  <Avatar className="medium bg-accent-2-light/10 mr-3">
                    <NiLinkBroken className="text-accent-2" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  className="w-40 flex-none"
                  primary={
                    <Typography component="p" variant="subtitle2" className="leading-4">
                      4. Social Media
                    </Typography>
                  }
                />
              </Box>
              <Button
                className="pointer-events-none self-center"
                size="tiny"
                color="success"
                variant="pastel"
                startIcon={<NiTriangleUp size={"tiny"} />}
              >
                1.1%
              </Button>
              <Typography component="p">1,240</Typography>
            </ListItemButton>
          </ListItem>

          <ListItem className="px-0 py-0">
            <ListItemButton classes={{ root: "group items-center justify-between" }}>
              <Box className="flex flex-row items-center">
                <ListItemAvatar>
                  <Avatar className="medium bg-accent-3-light/10 mr-3">
                    <NiWallet className="text-accent-3" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  className="w-40 flex-none"
                  primary={
                    <Typography component="p" variant="subtitle2" className="leading-4">
                      5. Advertising
                    </Typography>
                  }
                />
              </Box>
              <Button
                className="pointer-events-none self-center"
                size="tiny"
                color="success"
                variant="pastel"
                startIcon={<NiTriangleUp size={"tiny"} />}
              >
                3.4%
              </Button>
              <Typography component="p">947</Typography>
            </ListItemButton>
          </ListItem>

          <ListItem className="px-0 py-0">
            <ListItemButton classes={{ root: "group items-center justify-between" }}>
              <Box className="flex flex-row items-center">
                <ListItemAvatar>
                  <Avatar className="medium bg-accent-4-light/10 mr-3">
                    <NiEmail className="text-accent-4" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  className="w-40 flex-none"
                  primary={
                    <Typography component="p" variant="subtitle2" className="leading-4">
                      6. Email
                    </Typography>
                  }
                />
              </Box>
              <Button
                className="pointer-events-none self-center"
                size="tiny"
                color="error"
                variant="pastel"
                startIcon={<NiTriangleDown size={"tiny"} />}
              >
                2.8%
              </Button>
              <Typography component="p">288</Typography>
            </ListItemButton>
          </ListItem>
        </List>
      </CardContent>
    </Card>
  );
}

