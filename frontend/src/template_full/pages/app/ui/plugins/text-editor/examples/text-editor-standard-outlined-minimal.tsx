import "react-quill-new/dist/quill.snow.css";

import Icons from "quill/ui/icons";
import { useState } from "react";
import ReactDOMServer from "react-dom/server";
import ReactQuill from "react-quill-new";

import { Card, CardContent, Typography } from "@mui/material";

import NiCode from "@/template_full/icons/nexture/ni-code";
import NiDocumentCode from "@/template_full/icons/nexture/ni-document-code";
import NiLink from "@/template_full/icons/nexture/ni-link";
import NiList from "@/template_full/icons/nexture/ni-list";
import NiListCheck from "@/template_full/icons/nexture/ni-list-check";
import NiListNumber from "@/template_full/icons/nexture/ni-list-number";
import NiTextBold from "@/template_full/icons/nexture/ni-text-bold";
import NiTextItalic from "@/template_full/icons/nexture/ni-text-italic";
import NiTextQuote from "@/template_full/icons/nexture/ni-text-quote";
import NiTextStrikethrough from "@/template_full/icons/nexture/ni-text-strikethrough";

export default function TextEditorStandardOutlinedMinimal() {
  const [value, setValue] = useState("");
  Icons["bold"] = ReactDOMServer.renderToString(<NiTextBold size={"tiny"} />);
  Icons["italic"] = ReactDOMServer.renderToString(<NiTextItalic size={"tiny"} />);
  Icons["strike"] = ReactDOMServer.renderToString(<NiTextStrikethrough size={"tiny"} />);
  Icons["code-block"] = ReactDOMServer.renderToString(<NiCode size={"tiny"} />);
  Icons["code"] = ReactDOMServer.renderToString(<NiDocumentCode size={"tiny"} />);
  Icons["link"] = ReactDOMServer.renderToString(<NiLink size={"tiny"} />);
  Icons["blockquote"] = ReactDOMServer.renderToString(<NiTextQuote size={"tiny"} />);
  Icons["list"] = {
    ordered: ReactDOMServer.renderToString(<NiListNumber size={"tiny"} />),
    bullet: ReactDOMServer.renderToString(<NiList size={"tiny"} />),
    check: ReactDOMServer.renderToString(<NiListCheck size={"tiny"} />),
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h5" className="card-title">
          Standard Outlined Minimal
        </Typography>
        <ReactQuill
          modules={{
            toolbar: [
              ["bold", "italic", "strike"],
              ["blockquote", "code-block", "code"],
              [{ list: "ordered" }, { list: "bullet" }],
            ],
          }}
          placeholder="Composition"
          theme="snow"
          value={value}
          onChange={setValue}
          className="outlined [&_.ql-editor]:max-h-60 [&_.ql-editor]:min-h-40"
        />
      </CardContent>
    </Card>
  );
}

