import "yet-another-react-lightbox/styles.css";

import { useState } from "react";
import Lightbox from "yet-another-react-lightbox";

import { Card, CardContent, Typography } from "@mui/material";

import NiChevronLeftSmall from "@/icons/nexture/ni-chevron-left-small";
import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";
import NiCross from "@/icons/nexture/ni-cross";

export default function LightboxSingleImage() {
  const [open, setOpen] = useState(false);

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h5" className="card-title">
          Single Image
        </Typography>

        <img
          alt="lightbox image"
          src={"/images/products/product-2.jpg"}
          className="w-40 cursor-pointer rounded-lg"
          onClick={() => setOpen(true)}
        />

        <Lightbox
          open={open}
          close={() => setOpen(false)}
          slides={[{ src: "/images/products/product-2-large.jpg" }]}
          controller={{
            closeOnBackdropClick: true,
          }}
          render={{
            iconPrev: () => <NiChevronLeftSmall size={"large"} />,
            iconNext: () => <NiChevronRightSmall size={"large"} />,
            iconClose: () => <NiCross size={"large"} />,
          }}
        />
      </CardContent>
    </Card>
  );
}
