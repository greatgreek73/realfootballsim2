import { useState } from "react";

import { Box, Card, CardContent, Grid, Rating, Typography } from "@mui/material";

import NiStar from "@/template_full/icons/nexture/ni-star";

export default function RatingHover() {
  const labels: { [index: string]: string } = {
    0.5: "Useless",
    1: "Useless+",
    1.5: "Poor",
    2: "Poor+",
    2.5: "Ok",
    3: "Ok+",
    3.5: "Good",
    4: "Good+",
    4.5: "Excellent",
    5: "Excellent+",
  };
  function getLabelText(value: number) {
    return `${value} Star${value !== 1 ? "s" : ""}, ${labels[value]}`;
  }
  const [valueLabel, setValueLabel] = useState<number | null>(2);
  const [hoverLabel, setHoverLabel] = useState(-1);

  return (
    <Grid size={12}>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h5" className="card-title">
            Hover Feedback
          </Typography>
          <Box className="flex flex-row items-center">
            <Rating
              name="hover-feedback"
              value={valueLabel}
              precision={0.5}
              getLabelText={getLabelText}
              onChange={(_event, newValue) => {
                setValueLabel(newValue);
              }}
              onChangeActive={(_event, newHover) => {
                setHoverLabel(newHover);
              }}
              icon={<NiStar variant="contained" size="medium" className="contained" />}
              emptyIcon={<NiStar size="medium" className="outlined" />}
            />
            {valueLabel !== null && <Box className="ml-1">{labels[hoverLabel !== -1 ? hoverLabel : valueLabel]}</Box>}
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
}

