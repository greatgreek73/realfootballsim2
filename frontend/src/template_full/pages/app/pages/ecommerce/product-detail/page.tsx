import ProductDetailAttributes from "./sections/product-detail-attributes";
import ProductDetailInfo from "./sections/product-detail-info";
import ProductDetailInventory from "./sections/product-detail-inventory";
import ProductDetailMedia from "./sections/product-detail-media";
import ProductDetailPrice from "./sections/product-detail-price";
import ProductDetailSummary from "./sections/product-detail-summary";
import { SyntheticEvent, useState } from "react";
import { Link } from "react-router-dom";

import {
  Box,
  Breadcrumbs,
  Button,
  ButtonGroup,
  Fade,
  Grid,
  Menu,
  MenuItem,
  PopoverVirtualElement,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from "@mui/material";

import NiChartPie from "@/template_full/icons/nexture/ni-chart-pie";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import NiFloppyDisk from "@/template_full/icons/nexture/ni-floppy-disk";
import NiMessages from "@/template_full/icons/nexture/ni-messages";
import NiPenSquare from "@/template_full/icons/nexture/ni-pen-square";
import NiSendUpRight from "@/template_full/icons/nexture/ni-send-up-right";
import { cn } from "@/template_full/lib/utils";

export default function Page() {
  const [anchorEl, setAnchorEl] = useState<EventTarget | Element | PopoverVirtualElement | null>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: Event | SyntheticEvent) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const [tabValue, setTabValue] = useState("Edit");

  const handleTabChange = (_event: SyntheticEvent, newValue: string) => {
    setTabValue(newValue);
  };

  function TabWithTooltip(props: any) {
    const tooltip = props.tooltip;

    return (
      <Tooltip title={tooltip}>
        <Tab {...props} />
      </Tooltip>
    );
  }

  return (
    <Grid container spacing={5} className="w-full" size={12}>
      <Grid container spacing={2.5} className="w-full" size={12}>
        <Grid size={{ xs: 12, md: "grow" }}>
          <Typography variant="h1" component="h1" className="mb-0">
            Stretchy
          </Typography>
          <Breadcrumbs>
            <Link color="inherit" to="/dashboards/default">
              Home
            </Link>
            <Link color="inherit" to="/pages">
              Pages
            </Link>
            <Link color="inherit" to="/pages/ecommerce">
              Ecommerce
            </Link>
            <Typography variant="body2">Stretchy</Typography>
          </Breadcrumbs>
        </Grid>

        <Grid size={{ xs: 12, md: "auto" }} className="flex flex-row items-start gap-2">
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            textColor="primary"
            indicatorColor="primary"
            className="bg-background-paper shadow-darker-xs outline-line mb-0 rounded-md outline -outline-offset-1 backdrop-blur-xs"
            slotProps={{
              list: {
                className: "flex flex-row px-2 py-0.25",
              },
            }}
          >
            <TabWithTooltip
              tooltip="Edit"
              value="Edit"
              label={<NiPenSquare size={"medium"} />}
              className="hover:text-primary border-none! px-1.5! hover:bg-transparent!"
            />
            <TabWithTooltip
              tooltip="Analytics"
              value="Analytics"
              label={<NiChartPie size={"medium"} />}
              className="hover:text-primary border-none! px-1.5! hover:bg-transparent!"
            />
            <TabWithTooltip
              tooltip="Comments"
              value="Comments"
              label={<NiMessages size={"medium"} />}
              className="hover:text-primary border-none! px-1.5! hover:bg-transparent!"
            />
          </Tabs>

          <Tooltip title="Save">
            <Button className="icon-only surface-standard" color="grey" variant="surface">
              <NiFloppyDisk size={"medium"} />
            </Button>
          </Tooltip>

          <ButtonGroup size="medium" variant="surface" color="grey" className="surface-standard">
            <Button variant="surface" className="surface-standard" startIcon={<NiSendUpRight size={"medium"} />}>
              Publish
            </Button>
            <Button className="icon-only surface-standard" variant="surface" onClick={handleClick}>
              <NiChevronRightSmall size={"medium"} className={cn("transition-transform", open && "rotate-90")} />
            </Button>
          </ButtonGroup>

          <Menu
            anchorEl={anchorEl as Element}
            open={open}
            onClose={handleClose}
            className="mt-1"
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "right",
            }}
            transformOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
            slots={{
              transition: Fade,
            }}
          >
            <MenuItem>Save</MenuItem>
            <MenuItem>Draft</MenuItem>
          </Menu>
        </Grid>
      </Grid>
      <Grid container size={12}>
        <Grid size={{ xl: 8, xs: 12 }}>
          <ProductDetailInfo />
          <ProductDetailPrice />
          <ProductDetailInventory />
          <ProductDetailAttributes />

          <Box className="flex flex-row gap-2">
            <ButtonGroup size="medium" variant="surface" color="grey" className="surface-standard">
              <Button variant="surface" className="surface-standard" startIcon={<NiSendUpRight size={"medium"} />}>
                Publish
              </Button>
              <Button className="icon-only surface-standard" variant="surface">
                <NiChevronRightSmall size={"medium"} className={cn("transition-transform", open && "rotate-90")} />
              </Button>
            </ButtonGroup>
            <Tooltip title="Save">
              <Button className="icon-only surface-standard" color="grey" variant="surface">
                <NiFloppyDisk size={"medium"} />
              </Button>
            </Tooltip>
          </Box>
        </Grid>

        <Grid size={{ xl: 4, xs: 12 }}>
          <ProductDetailSummary />
          <ProductDetailMedia />
        </Grid>
      </Grid>
    </Grid>
  );
}

