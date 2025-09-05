import "yet-another-react-lightbox/plugins/thumbnails.css";
import "yet-another-react-lightbox/styles.css";

import { useState } from "react";
import Lightbox from "yet-another-react-lightbox";
import Thumbnails from "yet-another-react-lightbox/plugins/thumbnails";

import { Card, CardContent, Grid, Typography } from "@mui/material";

import NiChevronLeftSmall from "@/template_full/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import NiCross from "@/template_full/icons/nexture/ni-cross";
import NiPause from "@/template_full/icons/nexture/ni-pause";
import NiPlay from "@/template_full/icons/nexture/ni-play";

const largeImages = [
  {
    src: "/images/products/product-2-large.jpg",
  },
  {
    src: "/images/products/product-3-large.jpg",
  },
  {
    src: "/images/products/product-6-large.jpg",
  },
  {
    src: "/images/products/product-10-large.jpg",
  },
];
const smallImages = [
  "/images/products/product-2.jpg",
  "/images/products/product-3.jpg",
  "/images/products/product-6.jpg",
  "/images/products/product-10.jpg",
];

export default function LightboxThumbnails() {
  const [index, setIndex] = useState(-1);

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h5" className="card-title">
          Thumbnails
        </Typography>

        <Grid size={12} container spacing={2.5}>
          {smallImages.map((image, index) => {
            return (
              <Grid size={"auto"} key={index}>
                <img
                  alt="lightbox image"
                  src={image}
                  className="w-40 cursor-pointer rounded-lg"
                  onClick={() => setIndex(index)}
                />
              </Grid>
            );
          })}
        </Grid>

        <Lightbox
          index={index}
          open={index >= 0}
          close={() => setIndex(-1)}
          slides={largeImages}
          controller={{
            closeOnBackdropClick: true,
          }}
          render={{
            iconPrev: () => <NiChevronLeftSmall size={"large"} />,
            iconNext: () => <NiChevronRightSmall size={"large"} />,
            iconClose: () => <NiCross size={"large"} />,
            iconSlideshowPlay: () => <NiPlay size={"large"} />,
            iconSlideshowPause: () => <NiPause size={"large"} />,
          }}
          plugins={[Thumbnails]}
        />
      </CardContent>
    </Card>
  );
}

