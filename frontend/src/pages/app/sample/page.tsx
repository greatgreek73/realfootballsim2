import { Box, Card, CardContent, Stack, Typography } from "@mui/material";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";

export default function SamplePage() {
  const hero = (
    <HeroBar
      title="Sample Layout"
      subtitle="This page demonstrates the default PageShell template"
      tone="teal"
      kpis={[
        { label: "Sections", value: "Hero + Main + Aside" },
        { label: "Status", value: "Ready" },
        { label: "Updated", value: "Today" },
        { label: "Owner", value: "Design system" },
      ]}
    />
  );

  const mainContent = (
    <Box sx={{ display: "flex", height: "100%" }}>
      <Card sx={{ flex: 1, display: "flex" }}>
        <CardContent sx={{ flex: 1 }}>
          <Stack spacing={1.5}>
            <Typography variant="h6">Main content area</Typography>
            <Typography variant="body2" color="text.secondary">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum vel mi vel dui cursus
              bibendum. Donec vitae odio ut velit fermentum tempor. Etiam a facilisis nunc. Sed vel lectus at
              tortor consectetur imperdiet. Nulla bibendum, tellus nec fermentum consectetur, felis eros
              vulputate nunc, nec hendrerit velit turpis sed velit. Curabitur in tincidunt metus, vitae
              facilisis felis. Maecenas ut maximus ligula, vitae aliquet orci. Aenean ac turpis ante. Aenean
              pretium maximus mauris, sed vulputate nisi vulputate nec. Phasellus feugiat, odio at imperdiet
              tristique, lectus dolor faucibus ligula, id gravida purus sem in risus.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. In hac habitasse platea dictumst.
              Maecenas mattis erat vitae tellus malesuada, at mattis lacus posuere. Mauris ultrices elementum
              lacus, eget tincidunt lacus auctor id. Proin eget purus lacus. Maecenas pulvinar quam sit amet
              lorem commodo congue. Quisque interdum risus non sapien bibendum, eget bibendum neque
              condimentum. Sed aliquet, lacus at tempus condimentum, sem turpis fermentum ligula, eu viverra
              tortor justo sit amet lectus. Vestibulum sed sapien consequat, ullamcorper urna et, vestibulum
              lectus.
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );

  const asideContent = (
    <Box sx={{ display: "flex", height: "100%" }}>
      <Card sx={{ flex: 1, display: "flex" }}>
        <CardContent sx={{ flex: 1 }}>
          <Typography variant="h6" gutterBottom>
            Aside panel
          </Typography>
          <Typography variant="body2" color="text.secondary">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum vel mi vel dui cursus bibendum.
          Donec vitae odio ut velit fermentum tempor. Etiam a facilisis nunc. Sed vel lectus at tortor
          consectetur imperdiet. Nulla bibendum, tellus nec fermentum consectetur, felis eros vulputate nunc,
          nec hendrerit velit turpis sed velit. Curabitur in tincidunt metus, vitae facilisis felis. Maecenas
          ut maximus ligula, vitae aliquet orci. Aenean ac turpis ante. Aenean pretium maximus mauris, sed
          vulputate nisi vulputate nec.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras nec neque ac sapien sagittis fringilla
          in in ligula. Suspendisse potenti. Nullam eget pellentesque tellus. Ut porta eros at consectetur
          lacinia. Integer ut fermentum neque. Nulla in enim vel mauris laoreet faucibus vitae vitae arcu.
        </Typography>
      </CardContent>
    </Card>
  </Box>
  );

  return <PageShell hero={hero} main={mainContent} aside={asideContent} />;
}
