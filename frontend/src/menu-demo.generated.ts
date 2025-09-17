import { MenuItem } from "@/types/types";

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

const routeKeys = Object.keys(modules).map(keyToRoute);
const routeSet = new Set(routeKeys);

const root: Map<string, Node> = new Map();

for (const route of routeSet) {
  const segments = route.split("/").filter(Boolean);
  if (!segments.length) continue;

  const topSegment = segments[0];
  if (!ALLOWED_TOP.has(topSegment)) continue;

  const topNode = ensureRootChild(root, topSegment);

  let cursor = topNode;
  let currentPath = "";

  segments.forEach((segment, index) => {
    currentPath += "/" + segment;

    if (index === 0) {
      if (routeSet.has(currentPath)) cursor.href = currentPath;
      return;
    }

    cursor = ensureChild(cursor, segment);
    if (routeSet.has(currentPath)) cursor.href = currentPath;
  });
}

export const DEMO_FULL_ITEMS: MenuItem[] = TOP_GROUPS_ORDER.flatMap((segment) => {
  const node = root.get(segment);
  if (!node) return [];
  const mapped = nodeToMenu(node, 0);
  return mapped ? [mapped] : [];
});

function keyToRoute(key: string): string {
  return key.replace(/^\.\/pages\/app/, "").replace(/\/page\.tsx$/, "");
}

function ensureRootChild(tree: Map<string, Node>, name: string): Node {
  let existing = tree.get(name);
  if (!existing) {
    existing = { name, children: new Map() };
    tree.set(name, existing);
  }
  if (!existing.children) existing.children = new Map();
  return existing;
}

function ensureChild(parent: Node, name: string): Node {
  if (!parent.children) parent.children = new Map();
  let existing = parent.children.get(name);
  if (!existing) {
    existing = { name, children: new Map() };
    parent.children.set(name, existing);
  }
  if (!existing.children) existing.children = new Map();
  return existing;
}

function nodeToMenu(node: Node, depth: number): MenuItem | null {
  const label = pretty(node.name);
  const children =
    node.children &&
    Array.from(node.children.values())
      .map((child) => nodeToMenu(child, depth + 1))
      .filter((child): child is MenuItem => !!child)
      .sort((a, b) => a.label.localeCompare(b.label));

  if (!node.href && (!children || children.length === 0)) {
    return null;
  }

  const item: MenuItem = {
    id: node.name,
    label,
  };

  if (depth === 0 && ICONS[node.name]) {
    item.icon = ICONS[node.name] as any;
  }

  if (node.href) {
    item.href = node.href;
  }

  if (children && children.length) {
    item.children = children;
  }

  return item;
}

function pretty(name: string): string {
  if (LABEL_OVERRIDES[name]) return LABEL_OVERRIDES[name];
  return name
    .split("-")
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(" ");
}
