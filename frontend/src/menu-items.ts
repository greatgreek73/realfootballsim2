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
      { id: "players-list", label: "Players", href: "/my-club/players" },
      { id: "players-create", label: "Create Player", href: "/my-club/players/create" },
    ],
  },
  {
    id: "matches",
    icon: "NiCalendar",
    label: "Matches",
    color: "text-primary",
    href: "/matches",
    children: [
      { id: "matches-list", label: "All Matches", href: "/matches" },
      { id: "matches-create", label: "Schedule Match", href: "/matches/create" },
    ],
  },
  {
    id: "transfers",
    icon: "NiStructure",
    label: "Transfers",
    color: "text-primary",
    href: "/transfers",
    children: [
      { id: "transfers-market", label: "Market", href: "/transfers" },
      { id: "transfers-create", label: "Create Listing", href: "/transfers/create" },
      { id: "transfers-my", label: "My Deals", href: "/transfers/my" },
      { id: "transfers-history", label: "History", href: "/transfers/history" },
    ],
  },
  {
    id: "single-menu",
    icon: "NiDocumentFull",
    label: "menu-single-menu",
    color: "text-primary",
    href: "/single-menu",
  },

  {
    id: "demo",
    icon: "NiHome",
    label: "Demo",
    color: "text-primary",
    children: [
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


