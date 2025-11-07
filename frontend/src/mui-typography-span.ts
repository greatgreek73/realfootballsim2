import { createTheme } from "@mui/material/styles";

const typographySpanTheme = createTheme({
  components: {
    MuiTypography: {
      defaultProps: {
        variantMapping: {
          body1: "span",
          body2: "span",
        },
      },
    },
    MuiListItemText: {
      defaultProps: {
        primaryTypographyProps: { component: "span" },
        secondaryTypographyProps: { component: "span" },
      },
    },
  },
});

export default typographySpanTheme;
