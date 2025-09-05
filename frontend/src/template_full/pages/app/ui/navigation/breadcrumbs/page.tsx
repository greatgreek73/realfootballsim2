import { MouseEvent, useState } from "react";
import { Link } from "react-router-dom";

import { Breadcrumbs, Button, Card, CardContent, Menu, MenuItem, Typography } from "@mui/material";
import { Grid } from "@mui/material";

import NiCatalog from "@/template_full/icons/nexture/ni-catalog";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import NiEllipsisHorizontal from "@/template_full/icons/nexture/ni-ellipsis-horizontal";
import NiHome from "@/template_full/icons/nexture/ni-home";
import NiScreen from "@/template_full/icons/nexture/ni-screen";

export default function Page() {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: MouseEvent<HTMLButtonElement> | null) => {
    if (event) {
      setAnchorEl(event.currentTarget);
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Breadcrumbs
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/navigation">
            Navigation
          </Link>
          <Typography variant="body2">Breadcrumbs</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Basic
            </Typography>

            <Breadcrumbs>
              <Link to="/#public">MUI</Link>
              <Link to="/#public">Core</Link>
              <Typography variant="body2">Breadcrumbs</Typography>
            </Breadcrumbs>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Active Last Breadcrumb
            </Typography>

            <Breadcrumbs>
              <Link to="/#public">MUI</Link>
              <Link to="/#public">Core</Link>
              <Link to="/#public">Breadcrumbs</Link>
            </Breadcrumbs>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Custom Separator
            </Typography>

            <Breadcrumbs separator="-">
              <Link to="/#public">MUI</Link>
              <Link to="/#public">Core</Link>
              <Link to="/#public">Breadcrumbs</Link>
            </Breadcrumbs>

            <Breadcrumbs separator="›">
              <Link to="/#public">MUI</Link>
              <Link to="/#public">Core</Link>
              <Link to="/#public">Breadcrumbs</Link>
            </Breadcrumbs>

            <Breadcrumbs separator={<NiChevronRightSmall size="small" />}>
              <Link to="/#public">MUI</Link>
              <Link to="/#public">Core</Link>
              <Link to="/#public">Breadcrumbs</Link>
            </Breadcrumbs>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Breadcrumbs with Icons
            </Typography>

            <Breadcrumbs aria-label="breadcrumb">
              <Link className="flex items-center" to="/#public">
                <NiHome className="mr-1" size="small" />
                MUI
              </Link>
              <Link className="flex items-center" to="/#public">
                <NiScreen className="mr-1" size="small" />
                Core
              </Link>
              <Typography className="flex items-center">
                <NiCatalog className="mr-1" size="small" />
                Breadcrumb
              </Typography>
            </Breadcrumbs>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Collapsed
            </Typography>
            <Breadcrumbs maxItems={2}>
              <Link to="/#public">Home</Link>
              <Link to="/#public">Catalog</Link>
              <Link to="/#public">Accessories</Link>
              <Link to="/#public">New Collection</Link>
              <Typography>Belts</Typography>
            </Breadcrumbs>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" component="h5" className="card-title">
              Condensed
            </Typography>
            <Menu anchorEl={anchorEl} open={open} onClose={handleClose} aria-labelledby="with-menu-demo-breadcrumbs">
              <MenuItem onClick={handleClose}>Breadcrumb 2</MenuItem>
              <MenuItem onClick={handleClose}>Breadcrumb 3</MenuItem>
              <MenuItem onClick={handleClose}>Breadcrumb 4</MenuItem>
            </Menu>
            <Breadcrumbs aria-label="breadcrumbs">
              <Link color="primary" to="/#condensed-with-menu">
                Breadcrumb 1
              </Link>
              <Button
                onClick={handleClick}
                className="icon-only py-0.5!"
                size="tiny"
                color="grey"
                variant="text"
                startIcon={<NiEllipsisHorizontal size={"small"} />}
              />
              <Link color="primary" to="/#condensed-with-menu">
                Breadcrumb 5
              </Link>
              <Link color="primary" to="/#condensed-with-menu">
                Breadcrumb 6
              </Link>
            </Breadcrumbs>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

