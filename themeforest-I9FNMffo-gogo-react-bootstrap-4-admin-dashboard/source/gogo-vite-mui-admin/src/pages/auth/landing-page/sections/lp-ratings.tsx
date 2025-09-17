import { useTranslation } from "react-i18next";

import { Card, CardContent, FormGroup, FormLabel, Rating } from "@mui/material";

import NiChef from "@/icons/nexture/ni-chef";
import NiDrink from "@/icons/nexture/ni-drink";

export default function LPRatings() {
  const { t } = useTranslation();

  return (
    <Card>
      <CardContent>
        <FormGroup>
          <FormLabel component="label">{t("landing-drinks")}</FormLabel>
          <Rating
            defaultValue={4}
            max={5}
            icon={<NiDrink variant="contained" size="medium" className="contained text-secondary!" />}
            emptyIcon={<NiDrink size="medium" className="outlined" />}
          />
        </FormGroup>
        <FormGroup className="mb-0">
          <FormLabel component="label">{t("landing-food")}</FormLabel>
          <Rating
            defaultValue={5}
            max={5}
            icon={<NiChef variant="contained" size="medium" className="contained text-accent-1!" />}
            emptyIcon={<NiChef size="medium" className="outlined" />}
          />
        </FormGroup>
      </CardContent>
    </Card>
  );
}
