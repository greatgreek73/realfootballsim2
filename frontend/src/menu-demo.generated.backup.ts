import { MenuItem } from "@/types/types";

// Discover pages under src/pages/app/**/page.tsx
const modules = import.meta.glob("./pages/app/**/page.tsx");

type Node = { name: string; href?: string; children?: Map<string, Node> };

const TOP_GROUPS_ORDER = ["dashboards", "ui", "pages", "docs", "menu-levels"] as const;
const ALLOWED_TOP = new Set(TOP_GROUPS_ORDER);

const LABEL_OVERRIDES: Record<string, string> = {
  ui: "UI",
  docs: "Docs",
  pages: "Pages",
  "menu-levels": "Menu Levels",
  dashboards: "Dashboards",
  "data-display": "Data Display",
  "floating-action-button": "Floating Action Button",
  "date-time-picker": "Date & Time Picker",
  "mui-x": "MUI X",
};

const ICONS: Record<string, string> = {
  dashboards: "NiHome",
  ui: "NiController",
  pages: "NiScreen",
  docs: "NiDocumentFull",
  "menu-levels": "NiLayers",
};

function pretty(name: string): string {
  if (LABEL_OVERRIDES[name]) return LABEL_OVERRIDES[name];
  return name.split("-").map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(" " );
}

// '../pages/app/<route>/page.tsx' NOT used; keys come as './pages/app/...'
function keyToRoute(k: string): string {
  return k.replace(/^\.\/pages\/app/, "").replace(/\/page\.tsx$/, "");
}

function ensureChild(parent: Node, childName: string): Node {
  if (!parent.children) parent.children = new Map();
  const existing = parent.children.get(childName);
  if (existing) return existing;
  const n: Node = { name: childName };
  parent.children.set(childName, n);
  return n;
}

const routes = Object.keys(modules).map(keyToRoute); // '/ui/inputs/autocomplete' etc.

const root: Map<string, Node> = new Map();
for (const r of routes) {
  const segs = r.split("/").filter(Boolean);
  if (!segs.length) continue;
  const top = segs[0];
  if (!ALLOWED_TOP.has(top)) continue;

  const topNode = root.get(top) ?? (() => { const n: Node = { name: top }; root.set(top, n); return n; })();

  let acc = "";
  let current = topNode;
  for (let i = 0; i < segs.length; i++) {
    acc += "/" + segs[i];
    if (i > 0) current = ensureChild(current, segs[i]);
    if (routes.includes(acc)) current.href = acc;
  }
}

function nodeToMenu(n: Node, depth: number): MenuItem {
  const item: MenuItem = { id: n.name, label: pretty(n.name) } as any;
  if (depth === 0 && ICONS[n.name]) (item as any).icon = ICONS[n.name];
  if (n.href) (item as any).href = n.href;
  if (n.children?.size) {
    const kids = Array.from(n.children.values())
      .sort((a, b) => pretty(a.name).localeCompare(pretty(b.name)));
    (item as any).children = kids.map(c => nodeToMenu(c, depth + 1));
  }
  return item;
}

const topNodes = TOP_GROUPS_ORDER.map(name => root.get(name)).filter(Boolean) as Node[];
export const DEMO_FULL_ITEMS: MenuItem[] = topNodes.map(n => nodeToMenu(n, 0));

