import TextFieldFilled from "./examples/text-field-filled";
import TextFieldFormProps from "./examples/text-field-form-props";
import TextFieldIcons from "./examples/text-field-icons";
import TextFieldInputAdornments from "./examples/text-field-input-adornments";
import TextFieldMultiline from "./examples/text-field-multiline";
import TextFieldOutlined from "./examples/text-field-outlined";
import TextFieldStandard from "./examples/text-field-standard";
import TextFieldStandardOutlined from "./examples/text-field-standard-outlined";
import TextFieldValidation from "./examples/text-field-validation";
import { Link } from "react-router-dom";

import { Breadcrumbs, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function TextFieldPage() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Text Field
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/inputs">
            Inputs
          </Link>
          <Typography variant="body2">Text Field</Typography>
        </Breadcrumbs>
      </Grid>
      <TextFieldStandard />
      <TextFieldStandardOutlined />
      <TextFieldFilled />
      <TextFieldOutlined />
      <TextFieldFormProps />
      <TextFieldValidation />
      <TextFieldMultiline />
      <TextFieldInputAdornments />
      <TextFieldIcons />
    </Grid>
  );
}

