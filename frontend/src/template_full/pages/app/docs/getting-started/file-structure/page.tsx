import DocsMenu from "../../sections/docs-menu";
import { useState } from "react";
import { Link } from "react-router-dom";
import SyntaxHighlighter from "react-syntax-highlighter";
import { atomOneDark, atomOneLight } from "react-syntax-highlighter/dist/esm/styles/hljs";

import { Box, Breadcrumbs, Button, Card, CardContent, Drawer, Tooltip, Typography } from "@mui/material";
import { Grid } from "@mui/material";

import NiListCircle from "@/template_full/icons/nexture/ni-list-circle";
import { useThemeContext } from "@/template_full/theme/theme-provider";

const MenuContent = () => {
  return (
    <Box className="flex flex-col gap-4">
      <DocsMenu selectedID="docs-file-structure" />
    </Box>
  );
};

export default function DocsGettingStartedFileStructure() {
  const [openDrawer, setOpenDrawer] = useState(false);

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpenDrawer(newOpen);
  };

  const { isDarkMode } = useThemeContext();

  return (
    <Grid container spacing={5} className="items-start">
      <Grid size={"auto"} className="hidden pr-8 lg:flex">
        <MenuContent />
      </Grid>
      <Grid size={"grow"} spacing={5} container>
        <Grid size={12} spacing={2.5} container>
          <Grid size={{ xs: 12, md: "grow" }}>
            <Typography variant="h1" component="h1" className="mb-0">
              File Structure
            </Typography>
            <Breadcrumbs>
              <Link color="inherit" to="/dashboards/default">
                Home
              </Link>
              <Link color="inherit" to="/docs">
                Docs
              </Link>
              <Link color="inherit" to="/docs/getting-started">
                Getting Started
              </Link>
              <Typography variant="body2">File Structure</Typography>
            </Breadcrumbs>
          </Grid>
          <Grid size={{ xs: 12, md: "auto" }} className="lg:hidden">
            <Tooltip title="Table of Contents">
              <Button
                className="icon-only surface-standard"
                color="grey"
                variant="surface"
                onClick={toggleDrawer(true)}
              >
                <NiListCircle size={"medium"} />
              </Button>
            </Tooltip>
          </Grid>
        </Grid>

        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h5" className="card-title">
                Gogo-Vite MUI Admin Tailwind Template
              </Typography>
              <Typography variant="body1" component="p">
                Project structure and short explanations:
              </Typography>

              <Box className="bg-grey-20 syntax-highlighter mt-3 rounded-lg p-4">
                <SyntaxHighlighter
                  className="bg-transparent!"
                  language="asciidoc"
                  style={isDarkMode ? atomOneDark : atomOneLight}
                  codeTagProps={{ className: "border-none" }}
                  showLineNumbers
                >
                  {`+-- .husky                                // Husky auto-generated files
+-- public                                // Images, favicons and initial loader
    | 
    +-- favicon                           // Favicons of the project
    +-- images                            // Images of the project
    |-- initial-loader.css                // Loader styling of the project
    |-- initial-loader.js                 // Loader script of the project
+-- src                                   // Source code of the project
    | 
    +-- components                        // Components used project wide such as Header, Logo, Menu and so on
    +-- hooks                             // Basic hooks for menu, charts and screens
    +-- i18n                              // Multi-language files and translations
    +-- icons                             // Custom Nexture icons
    +-- lib                               // Utilities that are used throughout the project
    +-- pages                             // Pages and routes
    +-- style                             // All the CSS files
    +-- theme                             // Theme provider and MUI theme overrides
    +-- types                             // Custom types to extend MUI
    |-- App.tsx                           // The main layout of the application
    |-- config.ts                         // The main theme configuration
    |-- constants.ts                      // Variable definitions that are used in the theme
    |-- main.tsx                          // The initial file of the application
    |-- menu-items.ts                     // Menu data source
    |-- routes.tsx                        // Route definition
    |-- vite-env.d.ts                     // Vite environments
+-- worker                                // Cloudflare worker
|-- .env                                  // Variables for different environments
|-- .gitignore                            // Files that will be excluded from Git
|-- .lintstagedrc                         // Lint configuration for staged commits
|-- .nvmrc                                // Node version
|-- .prettierignore                       // Files that will be excluded from Prettier
|-- .prettierrc                           // Prettier configuration
|-- README.md                             // Details about the project
|-- eslint.config.ts                      // Eslint configuration
|-- index.html                            // HTML file that the application will load
|-- package.json                          // List of packages that are used in the project
|-- package.lock.json                     // List of package versions
|-- tailwind.config.ts                    // Tailwind configuration
|-- tsconfig.app.json                     // Typescript configuration for the app
|-- tsconfig.json                         // Typescript configuration
|-- tsconfig.node.json                    // Typescript configuration for the node
|-- tsconfig.node.json                    // Typescript configuration for the worker
|-- vercel.json                           // Vercel configuration
|-- vite.config.ts                        // Vite configuration
|-- worker-configuration.d.ts             // Worker configuration
|-- wrangler.jsonc                        // Wrangler configuration`}
                </SyntaxHighlighter>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Drawer open={openDrawer} anchor="right" onClose={toggleDrawer(false)}>
          <Box className="min-w-80 p-7">
            <MenuContent />
          </Box>
        </Drawer>
      </Grid>
    </Grid>
  );
}

