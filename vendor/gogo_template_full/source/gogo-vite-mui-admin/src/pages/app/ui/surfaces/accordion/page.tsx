import { Link } from "react-router-dom";

import { Box, Breadcrumbs, Card, CardContent, Typography } from "@mui/material";
import { Grid } from "@mui/material";
import Accordion from "@mui/material/Accordion";
import AccordionActions from "@mui/material/AccordionActions";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Button from "@mui/material/Button";

import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";
import NiChevronUpSmall from "@/icons/nexture/ni-chevron-up-small";
import NiCloudRain from "@/icons/nexture/ni-cloud-rain";
import NiCloudSnow from "@/icons/nexture/ni-cloud-snow";
import NiCloudThunder from "@/icons/nexture/ni-cloud-thunder";
import NiDrop from "@/icons/nexture/ni-drop";
import NiFire from "@/icons/nexture/ni-fire";
import NiFlash from "@/icons/nexture/ni-flash";
import NiScreen from "@/icons/nexture/ni-screen";
import NiTablet from "@/icons/nexture/ni-tablet";
import NiWatch from "@/icons/nexture/ni-watch";

export default function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Accordion
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/surfaces">
            Surfaces
          </Link>
          <Typography variant="body2">Accordion</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid container spacing={5}>
        <Grid size={6} className="h-full">
          <Card className="h-full">
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Basic
              </Typography>
              <Box>
                <Accordion defaultExpanded className="basic bordered">
                  <AccordionSummary expandIcon={<NiChevronUpSmall className="text-text-primary" />}>
                    <Typography component="span" variant="subtitle2">
                      Accordion First
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails className="text-text-secondary">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </AccordionDetails>
                </Accordion>
                <Accordion className="basic bordered">
                  <AccordionSummary expandIcon={<NiChevronUpSmall className="text-text-primary" />}>
                    <Typography component="span" variant="subtitle2">
                      Accordion Second
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails className="text-text-secondary">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </AccordionDetails>
                </Accordion>
                <Accordion className="basic bordered">
                  <AccordionSummary expandIcon={<NiChevronUpSmall className="text-text-primary" />}>
                    <Typography component="span" variant="subtitle2">
                      Accordion Actions
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails className="text-text-secondary">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </AccordionDetails>
                  <AccordionActions>
                    <Button>Cancel</Button>
                    <Button>Agree</Button>
                  </AccordionActions>
                </Accordion>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={6} className="h-full">
          <Card className="h-full">
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Icons
              </Typography>
              <Box>
                <Accordion defaultExpanded className="basic bordered">
                  <AccordionSummary expandIcon={<NiChevronUpSmall className="text-text-primary" />}>
                    <NiScreen className="text-primary" size={"medium"} />
                    <Typography component="span" variant="subtitle2" className="flex items-center pl-2">
                      Accordion First
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails className="text-text-secondary pl-8">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </AccordionDetails>
                </Accordion>
                <Accordion className="basic bordered">
                  <AccordionSummary expandIcon={<NiChevronUpSmall className="text-text-primary" />}>
                    <NiTablet className="text-secondary" size={"medium"} />
                    <Typography component="span" variant="subtitle2" className="flex items-center pl-2">
                      Accordion Second
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails className="text-text-secondary pl-8">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </AccordionDetails>
                </Accordion>
                <Accordion className="basic bordered">
                  <AccordionSummary expandIcon={<NiChevronUpSmall className="text-text-primary" />}>
                    <NiWatch className="text-accent-1" size={"medium"} />
                    <Typography component="span" variant="subtitle2" className="flex items-center pl-2">
                      Accordion Actions
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails className="text-text-secondary pl-8">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </AccordionDetails>
                  <AccordionActions>
                    <Button>Cancel</Button>
                    <Button>Agree</Button>
                  </AccordionActions>
                </Accordion>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={5}>
        <Grid size={6} className="h-full">
          <Card className="h-full">
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Filled
              </Typography>

              <Accordion className="mb-1.5" defaultExpanded>
                <AccordionSummary className="group">
                  <Button
                    component="div"
                    variant="pastel"
                    size="large"
                    color="text-primary"
                    className="full-width-button hover:text-primary group-aria-expanded:text-primary group-aria-expanded:rounded-b-none hover:bg-gray-500/10"
                    startIcon={<NiCloudRain size={"medium"} />}
                    endIcon={<NiChevronRightSmall size={20} className="accordion-rotate" />}
                  >
                    First Item
                  </Button>
                </AccordionSummary>
                <AccordionDetails className="bg-grey-500/10 mb-1.5 rounded-b-lg px-6 py-4">
                  <Typography variant="body1" component="p">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </Typography>
                </AccordionDetails>
              </Accordion>
              <Accordion className="mb-1.5">
                <AccordionSummary className="group">
                  <Button
                    component="div"
                    variant="pastel"
                    size="large"
                    color="text-primary"
                    className="full-width-button hover:text-primary group-aria-expanded:text-primary group-aria-expanded:rounded-b-none hover:bg-gray-500/10"
                    startIcon={<NiCloudThunder size={"medium"} />}
                    endIcon={<NiChevronRightSmall size={20} className="accordion-rotate" />}
                  >
                    Second Item
                  </Button>
                </AccordionSummary>
                <AccordionDetails className="bg-grey-500/10 mb-1.5 rounded-b-lg px-6 py-4">
                  <Typography variant="body1" component="p">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </Typography>
                </AccordionDetails>
              </Accordion>
              <Accordion className="mb-1.5">
                <AccordionSummary className="group">
                  <Button
                    component="div"
                    variant="pastel"
                    size="large"
                    color="text-primary"
                    className="full-width-button hover:text-primary group-aria-expanded:text-primary group-aria-expanded:rounded-b-none hover:bg-gray-500/10"
                    startIcon={<NiCloudSnow size={"medium"} />}
                    endIcon={<NiChevronRightSmall size={20} className="accordion-rotate" />}
                  >
                    Third Item
                  </Button>
                </AccordionSummary>
                <AccordionDetails className="bg-grey-500/10 mb-1.5 rounded-b-lg px-6 py-4">
                  <Typography variant="body1" component="p">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </Typography>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={6} className="h-full">
          <Card className="h-full">
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Outlined
              </Typography>

              <Accordion className="mb-1.5" defaultExpanded>
                <AccordionSummary className="group">
                  <Button
                    component="div"
                    variant="outlined"
                    size="large"
                    color="grey"
                    className="full-width-button border-grey-100 hover:text-primary group-aria-expanded:text-primary group-aria-expanded:rounded-b-none group-aria-expanded:border-b-transparent hover:bg-transparent"
                    startIcon={<NiFire size={"medium"} />}
                    endIcon={<NiChevronRightSmall size={20} className="accordion-rotate" />}
                  >
                    First Item
                  </Button>
                </AccordionSummary>
                <AccordionDetails className="border-grey-100 mb-1.5 rounded-b-lg border border-solid border-t-transparent px-6 py-4">
                  <Typography variant="body1" component="p">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </Typography>
                </AccordionDetails>
              </Accordion>
              <Accordion className="mb-1.5">
                <AccordionSummary className="group">
                  <Button
                    component="div"
                    variant="outlined"
                    size="large"
                    color="grey"
                    className="full-width-button border-grey-100 hover:text-primary group-aria-expanded:text-primary group-aria-expanded:rounded-b-none group-aria-expanded:border-b-transparent hover:bg-transparent"
                    startIcon={<NiDrop size={"medium"} />}
                    endIcon={<NiChevronRightSmall size={20} className="accordion-rotate" />}
                  >
                    Second Item
                  </Button>
                </AccordionSummary>
                <AccordionDetails className="border-grey-100 mb-1.5 rounded-b-lg border border-solid border-t-transparent px-6 py-4">
                  <Typography variant="body1" component="p">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </Typography>
                </AccordionDetails>
              </Accordion>
              <Accordion className="mb-1.5">
                <AccordionSummary className="group">
                  <Button
                    component="div"
                    variant="outlined"
                    size="large"
                    color="grey"
                    className="full-width-button border-grey-100 hover:text-primary group-aria-expanded:text-primary group-aria-expanded:rounded-b-none group-aria-expanded:border-b-transparent hover:bg-transparent"
                    startIcon={<NiFlash size={"medium"} />}
                    endIcon={<NiChevronRightSmall size={20} className="accordion-rotate" />}
                  >
                    Third Item
                  </Button>
                </AccordionSummary>
                <AccordionDetails className="border-grey-100 mb-1.5 rounded-b-lg border border-solid border-t-transparent px-6 py-4">
                  <Typography variant="body1" component="p">
                    My supervisor did not like the latest revision you gave me can you switch back to the first
                    revisionMy supervisor did not like the latest revision you gave me can.
                  </Typography>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={5} size={12}>
        <Grid size={12}>
          <Box className="mb-2.5 rounded-xl shadow-sm">
            <Accordion className="mb-1.5" defaultExpanded>
              <AccordionSummary className="group">
                <Card className="w-full shadow-none! group-aria-expanded:rounded-b-none">
                  <CardContent className="flex flex-row justify-between">
                    <Typography variant="h5" component="h5" className="mb-0">
                      Card First
                    </Typography>
                    <NiChevronRightSmall size={20} className="accordion-rotate" />
                  </CardContent>
                </Card>
              </AccordionSummary>
              <AccordionDetails className="bg-background-paper rounded-b-xl px-7 py-6 pt-0">
                <Typography variant="body1" component="p">
                  My supervisor did not like the latest revision you gave me can you switch back to the first revisionMy
                  supervisor did not like the latest revision you gave me can.
                </Typography>
              </AccordionDetails>
            </Accordion>
          </Box>
          <Box className="mb-2.5 rounded-xl shadow-sm">
            <Accordion className="mb-1.5">
              <AccordionSummary className="group">
                <Card className="w-full shadow-none! group-aria-expanded:rounded-b-none">
                  <CardContent className="flex flex-row justify-between">
                    <Typography variant="h5" component="h5" className="mb-0">
                      Card Second
                    </Typography>
                    <NiChevronRightSmall size={20} className="accordion-rotate" />
                  </CardContent>
                </Card>
              </AccordionSummary>
              <AccordionDetails className="bg-background-paper rounded-b-xl px-7 py-6 pt-0">
                <Typography variant="body1" component="p">
                  My supervisor did not like the latest revision you gave me can you switch back to the first revisionMy
                  supervisor did not like the latest revision you gave me can.
                </Typography>
              </AccordionDetails>
            </Accordion>
          </Box>
          <Box className="mb-2.5 rounded-xl shadow-sm">
            <Accordion className="mb-1.5">
              <AccordionSummary className="group">
                <Card className="w-full shadow-none! group-aria-expanded:rounded-b-none">
                  <CardContent className="flex flex-row justify-between">
                    <Typography variant="h5" component="h5" className="mb-0">
                      Card Third
                    </Typography>
                    <NiChevronRightSmall size={20} className="accordion-rotate" />
                  </CardContent>
                </Card>
              </AccordionSummary>
              <AccordionDetails className="bg-background-paper rounded-b-xl px-7 py-6 pt-0">
                <Typography variant="body1" component="p">
                  My supervisor did not like the latest revision you gave me can you switch back to the first revisionMy
                  supervisor did not like the latest revision you gave me can.
                </Typography>
              </AccordionDetails>
            </Accordion>
          </Box>
        </Grid>
      </Grid>
    </Grid>
  );
}
