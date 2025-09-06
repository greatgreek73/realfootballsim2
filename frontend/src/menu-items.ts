import { MenuItem } from "@/types/types";

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
    id: "template-demo",
    icon: "NiDashboard",
    label: "Template (Demo)",
    color: "text-primary",
    href: "/template",
    children: [
      { id: "template-default", icon: "NiDashboard", label: "Dashboards / Default", href: "/template/dashboards/default" },
      { id: "template-root", icon: "NiDocumentFull", label: "Template Root", href: "/template" },
      { id: "template-auth", icon: "NiDocumentFull", label: "Auth", href: "/template/auth" },
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
