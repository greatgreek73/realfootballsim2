import { Box, Button, Card, CardContent, Typography } from "@mui/material";

import IllustrationStorage from "@/template_full/icons/illustrations/illustration-storage";
import NiNext from "@/template_full/icons/nexture/ni-next";

export default function KnowledgeBaseTutorials() {
  return (
    <Card>
      <CardContent className="flex min-h-56 flex-col items-start justify-between">
        <Box className="flex w-full flex-col md:flex-row">
          <Box className="mb-4 w-full md:w-8/12 2xl:w-9/12">
            <Typography variant="h5" component="h5" className="card-title">
              Video Tutorials
            </Typography>
            <Typography
              variant="body1"
              component="p"
              className="text-text-secondary text-center md:text-left xl:max-w-md"
            >
              Learn quickly with our video tutorials! Whether you&apos;re a beginner or looking to enhance your skills,
              our guides make complex topics simple.
            </Typography>
          </Box>
          <Box className="flex w-full justify-center md:w-4/12 md:justify-end 2xl:w-3/12">
            <IllustrationStorage className="text-primary max-h-40 w-full object-contain"></IllustrationStorage>
          </Box>
        </Box>
        <Button
          className="mx-auto md:mx-0"
          size="medium"
          color="primary"
          variant="pastel"
          startIcon={<NiNext size={"medium"} />}
        >
          Watch Now
        </Button>
      </CardContent>
    </Card>
  );
}

