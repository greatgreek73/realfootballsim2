import SyntaxHighlighter from "react-syntax-highlighter";
import { atomOneDark, atomOneLight } from "react-syntax-highlighter/dist/esm/styles/hljs";

import { Accordion, AccordionDetails, AccordionSummary, Box, Card, CardContent, Typography } from "@mui/material";

import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import { useThemeContext } from "@/template_full/theme/theme-provider";

const FaqDetail = () => {
  const { isDarkMode } = useThemeContext();

  return (
    <Box className="mb-6">
      <Box>
        <Typography variant="h6" component="h6" className="mb-2">
          1. Issue description
        </Typography>
        <Typography variant="body1" component="p">
          Before diving into the development, familiarize yourself with the core technologies of web applications:
        </Typography>
        <br />
        <Typography variant="body1" component="ul">
          <Typography variant="body1" component="li">
            <Typography variant="subtitle1" component="span">
              HTML:
            </Typography>{" "}
            The structure and layout of your application.
          </Typography>
          <Typography variant="body1" component="li">
            <Typography variant="subtitle1" component="span">
              CSS:
            </Typography>{" "}
            The styling and design.
          </Typography>
          <Typography variant="body1" component="li">
            <Typography variant="subtitle1" component="span">
              JavaScript:
            </Typography>{" "}
            The functionality and interactivity.
          </Typography>
          <Typography variant="body1" component="li">
            <Typography variant="subtitle1" component="span">
              Frameworks/Libraries (Optional):
            </Typography>{" "}
            Tools like React, Angular, or Vue.js simplify development.
          </Typography>
        </Typography>
        <br />
      </Box>

      <Box>
        <Typography variant="h6" component="h6" className="mb-2">
          2. Context
        </Typography>
        <Typography variant="body1" component="p">
          To start coding, you need:
        </Typography>
        <br />
        <Typography variant="body1" component="ul">
          <Typography variant="body1" component="li">
            <Typography variant="subtitle1" component="span">
              Code Editor:
            </Typography>{" "}
            Use VS Code or Sublime Text for writing code.
          </Typography>
          <Typography variant="body1" component="li">
            <Typography variant="subtitle1" component="span">
              Browser:
            </Typography>{" "}
            Chrome, Firefox, or Edge for testing and debugging.
          </Typography>
          <Typography variant="body1" component="li">
            <Typography variant="subtitle1" component="span">
              Package Manager:
            </Typography>{" "}
            Install Node.js and npm (Node Package Manager) for managing dependencies.
          </Typography>
          <Typography variant="body1" component="li">
            <Typography variant="subtitle1" component="span">
              Version Control:
            </Typography>{" "}
            Use Git and GitHub to manage your codebase and collaborate.
          </Typography>
        </Typography>
        <br />
      </Box>

      <Box>
        <Typography variant="h6" component="h6" className="mb-2">
          3. Environment
        </Typography>
        <Typography variant="body1" component="p">
          Organize your web application with a clear and logical project structure. Keep essential files like HTML, CSS,
          and JavaScript separate, and use folders for assets such as images and fonts. A well-structured setup ensures
          maintainability and scalability as your application grows. Organize your files for a simple web application:
        </Typography>

        <Box className="bg-grey-20 syntax-highlighter mt-3 rounded-lg p-4">
          <SyntaxHighlighter
            className="bg-transparent!"
            language="javascript"
            style={isDarkMode ? atomOneDark : atomOneLight}
            codeTagProps={{ className: "border-none" }}
            showLineNumbers
          >
            {`my-web-app/
└── index.html    // Main HTML file
└── style.css     // CSS file
└── script.js     // JavaScript file
└── assets        // Images, fonts, etc.`}
          </SyntaxHighlighter>
        </Box>
        <br />
      </Box>

      <Box>
        <Typography variant="h6" component="h6" className="mb-2">
          4. Steps to Reproduce
        </Typography>
        <Typography variant="subtitle1">HTML:</Typography>
        <Box className="bg-grey-20 syntax-highlighter mt-3 rounded-lg p-4">
          <SyntaxHighlighter
            className="bg-transparent!"
            language="html"
            style={isDarkMode ? atomOneDark : atomOneLight}
            codeTagProps={{ className: "border-none" }}
            showLineNumbers
          >
            {`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Web App</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Welcome to My Web Application</h1>
  <button id="myButton">Click Me</button>
  <script src="script.js"></script>
</body>
</html>`}
          </SyntaxHighlighter>
        </Box>
        <br />

        <Typography variant="subtitle1">CSS:</Typography>
        <Box className="bg-grey-20 syntax-highlighter mt-3 rounded-lg p-4">
          <SyntaxHighlighter
            className="bg-transparent!"
            language="html"
            style={isDarkMode ? atomOneDark : atomOneLight}
            codeTagProps={{ className: "border-none" }}
            showLineNumbers
          >
            {`body {
  font-family: Arial, sans-serif;
  text-align: center;
  background-color: #f4f4f4;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}`}
          </SyntaxHighlighter>
        </Box>
        <br />

        <Typography variant="subtitle1">JS:</Typography>
        <Box className="bg-grey-20 syntax-highlighter mt-3 rounded-lg p-4">
          <SyntaxHighlighter
            className="bg-transparent!"
            language="html"
            style={isDarkMode ? atomOneDark : atomOneLight}
            codeTagProps={{ className: "border-none" }}
            showLineNumbers
          >
            {`document.getElementById("myButton").addEventListener("click", () => {
  alert("Button clicked!");
});`}
          </SyntaxHighlighter>
        </Box>
      </Box>
    </Box>
  );
};

export default function FaqContent() {
  return (
    <>
      <Box className="mb-2.5 rounded-xl shadow-sm">
        <Accordion className="mb-1.5" defaultExpanded>
          <AccordionSummary className="group">
            <Card className="w-full shadow-none! group-aria-expanded:rounded-b-none">
              <CardContent className="flex flex-row justify-between">
                <Typography variant="h5" component="h5" className="mb-0">
                  Initial Steps
                </Typography>
                <NiChevronRightSmall size={20} className="accordion-rotate" />
              </CardContent>
            </Card>
          </AccordionSummary>
          <AccordionDetails className="bg-background-paper rounded-b-xl px-7 py-6 pt-0">
            <FaqDetail />
          </AccordionDetails>
        </Accordion>
      </Box>
      <Box className="mb-2.5 rounded-xl shadow-sm">
        <Accordion className="mb-1.5">
          <AccordionSummary className="group">
            <Card className="w-full shadow-none! group-aria-expanded:rounded-b-none">
              <CardContent className="flex flex-row justify-between">
                <Typography variant="h5" component="h5" className="mb-0">
                  Manual Installation
                </Typography>
                <NiChevronRightSmall size={20} className="accordion-rotate" />
              </CardContent>
            </Card>
          </AccordionSummary>
          <AccordionDetails className="bg-background-paper rounded-b-xl px-7 py-6 pt-0">
            <FaqDetail />
          </AccordionDetails>
        </Accordion>
      </Box>
      <Box className="mb-2.5 rounded-xl shadow-sm">
        <Accordion className="mb-1.5">
          <AccordionSummary className="group">
            <Card className="w-full shadow-none! group-aria-expanded:rounded-b-none">
              <CardContent className="flex flex-row justify-between">
                <Typography variant="h5" component="h5" className="mb-0">
                  Configuration
                </Typography>
                <NiChevronRightSmall size={20} className="accordion-rotate" />
              </CardContent>
            </Card>
          </AccordionSummary>
          <AccordionDetails className="bg-background-paper rounded-b-xl px-7 py-6 pt-0">
            <FaqDetail />
          </AccordionDetails>
        </Accordion>
      </Box>
      <Box className="mb-2.5 rounded-xl shadow-sm">
        <Accordion className="mb-1.5">
          <AccordionSummary className="group">
            <Card className="w-full shadow-none! group-aria-expanded:rounded-b-none">
              <CardContent className="flex flex-row justify-between">
                <Typography variant="h5" component="h5" className="mb-0">
                  Advanced Use Cases
                </Typography>
                <NiChevronRightSmall size={20} className="accordion-rotate" />
              </CardContent>
            </Card>
          </AccordionSummary>
          <AccordionDetails className="bg-background-paper rounded-b-xl px-7 py-6 pt-0">
            <FaqDetail />
          </AccordionDetails>
        </Accordion>
      </Box>
    </>
  );
}

