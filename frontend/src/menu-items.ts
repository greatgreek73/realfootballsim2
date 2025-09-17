import { MenuItem } from "@/types/types";
import { DEMO_FULL_ITEMS } from "@/menu-demo.generated";

export const leftMenuItems: MenuItem[] = [
  {
    id: "squad",
    icon: "NiUsers",
    label: "Squad",
    color: "text-primary",
    href: "/my-club/players",
  },
  {
    id: "home",
    icon: "NiHome",
    label: "menu-home",
    color: "text-primary",
    href: "/my-club",
  },
  {
    id: "single-menu",
    icon: "NiDocumentFull",
    label: "menu-single-menu",
    color: "text-primary",
    href: "/single-menu",
  },

  // --- пїЅпїЅпїЅпїЅ а §пїЅпїЅпїЅ: Demo (пїЅпїЅа ­пїЅпїЅпїЅ пїЅгЇ«пїЅпїЅпїЅпїЅпїЅпїЅ и ЎпїЅпїЅпїЅпїЅ) ---
  {
    id: "demo",
    icon: "NiHome",
    label: "Demo",
    color: "text-primary",
    children: [
      // пїЅпїЅпїЅпїЅпїЅпїЅпҐ¬ в®«мЄ® аҐ пїЅм­® пїЅпїЅпїЅпїЅпїЅпїЅпїЅйЁҐ пїЅпїЅпїЅпїЅпїЅм­® пїЅпїЅа ­пїЅпїЅпїЅ пїЅпїЅпїЅпїЅ
      { id: "demo-dashboard-visual", label: "Dashboards: Visual", href: "/dashboards/visual" },
      { id: "demo-ui-avatar", label: "UI: Avatar", href: "/ui/data-display/avatar" },
      { id: "demo-docs-intro", label: "Docs: Introduction", href: "/docs/welcome/introduction" },
    ],
  },
  {
    id: "demo-full",
    icon: "NiLayers",
    label: "Demo (Full)",
    color: "text-primary",
    children: DEMO_FULL_ITEMS,
  },

  {
    id: "external-link",
    icon: "NiArrowUpRightSquare",
    label: "menu-external-link",
    color: "text-primary",
    href: "https://themeforest.net/",
    isExternalLink: true,
  },
];

export const leftMenuBottomItems: MenuItem[] = [
  { id: "settings", label: "menu-settings", href: "/settings", icon: "NiSettings" },
];
