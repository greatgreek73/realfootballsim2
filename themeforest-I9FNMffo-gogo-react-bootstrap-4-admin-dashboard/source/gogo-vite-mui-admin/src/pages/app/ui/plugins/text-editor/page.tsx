import TextEditorStandard from "./examples/text-editor-standard";
import TextEditorStandardMinimal from "./examples/text-editor-standard-minimal copy";
import TextEditorStandardOutlined from "./examples/text-editor-standard-outlined";
import TextEditorStandardOutlinedMinimal from "./examples/text-editor-standard-outlined-minimal";
import { Link } from "react-router-dom";

import { Breadcrumbs, Typography } from "@mui/material";
import { Grid } from "@mui/material";

export default function Page() {
  return (
    <Grid container spacing={5}>
      <Grid size={12} className="mb-2">
        <Typography variant="h1" component="h1" className="mb-0">
          Text Editor
        </Typography>
        <Breadcrumbs>
          <Link color="inherit" to="/dashboards/default">
            Home
          </Link>
          <Link color="inherit" to="/ui">
            UI Elements
          </Link>
          <Link color="inherit" to="/ui/plugins">
            Plugins
          </Link>
          <Typography variant="body2">Text Editor</Typography>
        </Breadcrumbs>
      </Grid>

      <Grid size={12}>
        <TextEditorStandard />
      </Grid>

      <Grid size={12}>
        <TextEditorStandardMinimal />
      </Grid>

      <Grid size={12}>
        <TextEditorStandardOutlined />
      </Grid>

      <Grid size={12}>
        <TextEditorStandardOutlinedMinimal />
      </Grid>
    </Grid>
  );
}
