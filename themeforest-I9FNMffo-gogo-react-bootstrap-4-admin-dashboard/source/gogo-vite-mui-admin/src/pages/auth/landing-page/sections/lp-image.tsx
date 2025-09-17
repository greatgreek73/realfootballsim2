import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Button, Card, CardContent, Paper, Typography } from "@mui/material";

import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";
import NiEllipsisHorizontal from "@/icons/nexture/ni-ellipsis-horizontal";
import { getThemeImage } from "@/lib/image-helper";
import { useThemeContext } from "@/theme/theme-provider";

export default function LPImage() {
  const { isDarkMode, theme } = useThemeContext();
  const { t } = useTranslation();
  const [image, setImage] = useState<string | null>(null);

  useEffect(() => {
    const imageUrl = getThemeImage({
      srcSet: ["product-7-horizontal.jpg", "product-7-horizontal-dark.jpg"],
      directory: "/images/products/",
      current: { isDarkMode, theme },
    });
    setImage(imageUrl);
  }, [isDarkMode, theme]);

  return (
    <Card className="group p-1">
      <CardContent className="p-0!">
        <Paper elevation={0} className="relative h-[140px] w-[200px] overflow-hidden rounded-2xl p-0">
          <Box className="absolute inset-0 z-1 flex flex-col justify-between bg-black/30 p-7 opacity-0 transition-opacity group-hover:opacity-100 group-hover:backdrop-blur-[1px]">
            <Typography variant="subtitle2" className="text-text-contrast">
              Boo Boo
            </Typography>
            <Box className="flex flex-row justify-between">
              <Button
                className="icon-only hover:text-primary! pr-4! pl-3!"
                size="small"
                color="grey"
                variant="pastel"
                startIcon={<NiChevronRightSmall size={"small"} />}
              >
                {t("landing-view")}
              </Button>
              <Box className="flex flex-row gap-2">
                <Button
                  className="icon-only hover:text-primary!"
                  size="small"
                  color="grey"
                  variant="pastel"
                  startIcon={<NiEllipsisHorizontal size={"small"} />}
                />
              </Box>
            </Box>
          </Box>
          {image && (
            <img
              width={162}
              height={120}
              alt="Product"
              className="relative z-0 h-full w-full scale-110 object-cover transition-transform group-hover:scale-100"
              src={image}
            />
          )}
        </Paper>
      </CardContent>
    </Card>
  );
}
