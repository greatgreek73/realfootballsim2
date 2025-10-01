import { MenuItem } from "@/types/types";
import { DEMO_FULL_ITEMS } from "@/menu-demo.generated";

export const leftMenuItems: MenuItem[] = [
  {
    id: "my-club",
    icon: "NiHome",
    label: "menu-home",
    color: "text-primary",
    href: "/my-club",
  },
  {
    id: "squad",
    icon: "NiUsers",
    label: "Squad",
    color: "text-primary",
    href: "/my-club/players",
    children: [
      { id: 'players-list',   label: 'Players',       href: '/my-club/players' },
      { id: 'players-create', label: 'Create Player', href: '/my-club/players/create' }
    ]
  },
  {
    id: "single-menu",
    icon: "NiDocumentFull",
    label: "menu-single-menu",
    color: "text-primary",
    href: "/single-menu",
  },

  // --- РїС—Р…РїС—Р…РїС—Р…РїС—Р… Р°В В§РїС—Р…РїС—Р…РїС—Р…: Demo (РїС—Р…РїС—Р…Р°В В­РїС—Р…РїС—Р…РїС—Р… РїС—Р…РіР‡В«РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РёВ РЋРїС—Р…РїС—Р…РїС—Р…РїС—Р…) ---
  {
    id: "demo",
    icon: "NiHome",
    label: "Demo",
    color: "text-primary",
    children: [
      // РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїТђВ¬ РІВ®В«РјР„В® Р°ТђВ РїС—Р…РјВ­В® РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…Р№РЃТђ РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РјВ­В® РїС—Р…РїС—Р…Р°В В­РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…
      { id: "demo-dashboard-visual", label: "Dashboards: Visual", href: "/dashboards/visual" },
      { id: "demo-ui-avatar", label: "UI: Avatar", href: "/ui/data-display/avatar" },
      { id: "demo-docs-intro", label: "Docs: Introduction", href: "/docs/welcome/introduction" },
    ],
  },
  {
    id: "demo-full",
    icon: "NiStructure",
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


