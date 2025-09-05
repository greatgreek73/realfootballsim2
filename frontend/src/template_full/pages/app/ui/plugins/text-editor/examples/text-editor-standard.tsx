import "react-quill-new/dist/quill.snow.css";

import Icons from "quill/ui/icons";
import { useState } from "react";
import ReactDOMServer from "react-dom/server";
import ReactQuill from "react-quill-new";

import { Card, CardContent, Typography } from "@mui/material";

import NiBrackets from "@/template_full/icons/nexture/ni-brackets";
import NiCode from "@/template_full/icons/nexture/ni-code";
import NiDocumentCode from "@/template_full/icons/nexture/ni-document-code";
import NiDocumentImage from "@/template_full/icons/nexture/ni-document-image";
import NiDocumentVideo from "@/template_full/icons/nexture/ni-document-video";
import NiEndLeftSmall from "@/template_full/icons/nexture/ni-end-left-small";
import NiEndRightSmall from "@/template_full/icons/nexture/ni-end-right-small";
import NiEraser from "@/template_full/icons/nexture/ni-eraser";
import NiLayout from "@/template_full/icons/nexture/ni-layout";
import NiLink from "@/template_full/icons/nexture/ni-link";
import NiList from "@/template_full/icons/nexture/ni-list";
import NiListCheck from "@/template_full/icons/nexture/ni-list-check";
import NiListNumber from "@/template_full/icons/nexture/ni-list-number";
import NiMenuLeft from "@/template_full/icons/nexture/ni-menu-left";
import NiMenuRight from "@/template_full/icons/nexture/ni-menu-right";
import NiPaintBucket from "@/template_full/icons/nexture/ni-paint-bucket";
import NiPaintRoller from "@/template_full/icons/nexture/ni-paint-roller";
import NiScriptSub from "@/template_full/icons/nexture/ni-script-sub";
import NiScriptSuper from "@/template_full/icons/nexture/ni-script-super";
import NiTextBold from "@/template_full/icons/nexture/ni-text-bold";
import NiTextCenter from "@/template_full/icons/nexture/ni-text-center";
import NiTextItalic from "@/template_full/icons/nexture/ni-text-italic";
import NiTextJustify from "@/template_full/icons/nexture/ni-text-justify";
import NiTextLeft from "@/template_full/icons/nexture/ni-text-left";
import NiTextQuote from "@/template_full/icons/nexture/ni-text-quote";
import NiTextRight from "@/template_full/icons/nexture/ni-text-right";
import NiTextStrikethrough from "@/template_full/icons/nexture/ni-text-strikethrough";
import NiTextUnderline from "@/template_full/icons/nexture/ni-text-underline";

export default function TextEditorStandard() {
  const [value, setValue] = useState("");
  Icons["bold"] = ReactDOMServer.renderToString(<NiTextBold />);
  Icons["italic"] = ReactDOMServer.renderToString(<NiTextItalic />);
  Icons["underline"] = ReactDOMServer.renderToString(<NiTextUnderline />);
  Icons["strike"] = ReactDOMServer.renderToString(<NiTextStrikethrough />);
  Icons["blockquote"] = ReactDOMServer.renderToString(<NiTextQuote />);
  Icons["code-block"] = ReactDOMServer.renderToString(<NiCode />);
  Icons["code"] = ReactDOMServer.renderToString(<NiDocumentCode />);
  Icons["color"] = ReactDOMServer.renderToString(<NiPaintRoller />);
  Icons["background"] = ReactDOMServer.renderToString(<NiPaintBucket />);
  Icons["clean"] = ReactDOMServer.renderToString(<NiEraser />);
  Icons["table"] = ReactDOMServer.renderToString(<NiLayout />);
  Icons["image"] = ReactDOMServer.renderToString(<NiDocumentImage />);
  Icons["video"] = ReactDOMServer.renderToString(<NiDocumentVideo />);
  Icons["formula"] = ReactDOMServer.renderToString(<NiBrackets />);
  Icons["link"] = ReactDOMServer.renderToString(<NiLink />);
  Icons["list"] = {
    ordered: ReactDOMServer.renderToString(<NiListNumber />),
    bullet: ReactDOMServer.renderToString(<NiList />),
    check: ReactDOMServer.renderToString(<NiListCheck />),
  };
  Icons["script"] = {
    sub: ReactDOMServer.renderToString(<NiScriptSub />),
    super: ReactDOMServer.renderToString(<NiScriptSuper />),
  };
  Icons["indent"] = {
    "-1": ReactDOMServer.renderToString(<NiMenuLeft />),
    "+1": ReactDOMServer.renderToString(<NiMenuRight />),
  };
  Icons["direction"] = {
    rtl: ReactDOMServer.renderToString(<NiEndLeftSmall />),
    "": ReactDOMServer.renderToString(<NiEndRightSmall />),
  };
  Icons["align"] = {
    "": ReactDOMServer.renderToString(<NiTextLeft />),
    center: ReactDOMServer.renderToString(<NiTextCenter />),
    right: ReactDOMServer.renderToString(<NiTextRight />),
    justify: ReactDOMServer.renderToString(<NiTextJustify />),
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h5" className="card-title">
          Standard
        </Typography>
        <ReactQuill
          modules={{
            toolbar: [
              [{ header: [1, 2, false] }],
              [{ align: "" }, { align: "center" }, { align: "right" }, { align: "justify" }],
              ["bold", "italic", "strike", "underline"],
              ["blockquote", "code-block", "code"],
              [{ list: "ordered" }, { list: "bullet" }, { list: "check" }],
              [{ script: "sub" }, { script: "super" }],
              [{ indent: "-1" }, { indent: "+1" }],
              [{ direction: "rtl" }],
              [{ color: [] }, { background: [] }],
              ["clean"],
              ["table"],
              ["image", "video"],
              ["formula"],
              ["link"],
            ],
          }}
          placeholder="Composition"
          theme="snow"
          value={value}
          onChange={setValue}
          className="standard [&_.ql-editor]:max-h-60 [&_.ql-editor]:min-h-40"
        />
      </CardContent>
    </Card>
  );
}

