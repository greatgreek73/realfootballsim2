import { MenuItem } from "@/types/types";

export const leftMenuItems: MenuItem[] = [
  {
    id: "home",
    icon: "NiHome",
    label: "menu-home",
    description: "menu-home-description",
    color: "text-primary",
    href: "/home",
    children: [
      {
        id: "home-sub",
        icon: "NiChartPie",
        label: "menu-home-sub",
        href: "/home/sub",
        description: "menu-home-sub-description",
      },
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
