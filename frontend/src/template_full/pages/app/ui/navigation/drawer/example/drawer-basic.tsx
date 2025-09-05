import { useState } from "react";

import { Box, Collapse } from "@mui/material";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";

import NiBinEmpty from "@/template_full/icons/nexture/ni-bin-empty";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronUpSmall from "@/template_full/icons/nexture/ni-chevron-up-small";
import NiDirectory from "@/template_full/icons/nexture/ni-directory";
import NiEmailOpen from "@/template_full/icons/nexture/ni-email-open";
import NiExclamationHexagon from "@/template_full/icons/nexture/ni-exclamation-hexagon";
import NiInbox from "@/template_full/icons/nexture/ni-inbox";
import NiSendRight from "@/template_full/icons/nexture/ni-send-right";
import NiSign from "@/template_full/icons/nexture/ni-sign";
import NiStar from "@/template_full/icons/nexture/ni-star";
import NiTag from "@/template_full/icons/nexture/ni-tag";

export default function DrawerBasic() {
  const [openCollapse, setOpenCollapse] = useState(true);
  const handleClickCollapse = () => {
    setOpenCollapse(!openCollapse);
  };

  const [openDrawer, setOpenDrawer] = useState(false);
  const toggleDrawer = (newOpen: boolean) => () => {
    setOpenDrawer(newOpen);
  };

  const drawerContent = (
    <Box className="w-80 p-4">
      <List>
        <ListItem disablePadding>
          <ListItemButton>
            <ListItemIcon>
              <NiInbox size="medium" />
            </ListItemIcon>
            <ListItemText primary="Inbox" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton>
            <ListItemIcon>
              <NiStar size="medium" />
            </ListItemIcon>
            <ListItemText primary="Starred" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton>
            <ListItemIcon>
              <NiSendRight size="medium" />
            </ListItemIcon>
            <ListItemText primary="Sent" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton>
            <ListItemIcon>
              <NiEmailOpen size="medium" />
            </ListItemIcon>
            <ListItemText primary="Drafts" />
          </ListItemButton>
        </ListItem>
      </List>
      <Divider />
      <ListItemButton onClick={handleClickCollapse}>
        <ListItemIcon>
          {openCollapse ? <NiChevronUpSmall size="medium" /> : <NiChevronDownSmall size="medium" />}
        </ListItemIcon>
        <ListItemText primary="More" />
      </ListItemButton>
      <Collapse in={openCollapse} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
          <ListItemButton>
            <ListItemIcon>{<NiDirectory size="medium" />}</ListItemIcon>
            <ListItemText primary="Categories" />
          </ListItemButton>
          <ListItemButton>
            <ListItemIcon>{<NiTag size="medium" />}</ListItemIcon>
            <ListItemText primary="Tags" />
          </ListItemButton>
          <ListItemButton>
            <ListItemIcon>{<NiSign size="medium" />}</ListItemIcon>
            <ListItemText primary="Labels" />
          </ListItemButton>
        </List>
      </Collapse>

      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton>
            <ListItemIcon>
              <NiBinEmpty size="medium" />
            </ListItemIcon>
            <ListItemText primary="Trash" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton component="a" href="#simple-list">
            <ListItemIcon>
              <NiExclamationHexagon size="medium" />
            </ListItemIcon>
            <ListItemText primary="Spam" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box>
      <Button variant="outlined" onClick={toggleDrawer(true)}>
        Open Drawer
      </Button>
      <Drawer open={openDrawer} onClose={toggleDrawer(false)}>
        {drawerContent}
      </Drawer>
    </Box>
  );
}

