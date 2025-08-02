import { memo, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation } from "react-router-dom";

import { Box, Button, Tooltip, Typography } from "@mui/material";

import NextureIcons from "@/icons/nexture-icons";
import { cn, isPathMatch } from "@/lib/utils";
import { MenuItem, MenuType } from "@/types/types";

type Props = {
  item: MenuItem;
  onSelect: (item: MenuItem) => void;
  isActive: boolean;
  menuType: MenuType;
  className?: string;
};

export const PrimaryItem = memo(function PrimaryItem({ item, onSelect, isActive, menuType, className }: Props) {
  const { t } = useTranslation();

  const { pathname } = useLocation();
  const selected = useMemo(() => {
    if (!item) return false;
    if (item.href && isPathMatch(pathname, item.href)) return true;
    if (item.children) return item.children.some((child) => child.href && isPathMatch(pathname, child.href));

    return false;
  }, [item, pathname]);

  const [tooltipOpen, setTooltipOpen] = useState(false);

  if (menuType !== MenuType.Minimal) {
    return (
      <Box
        className={cn(
          "hover:bg-grey-25/90 flex h-[5.5rem] w-24 cursor-pointer flex-col items-center justify-center gap-1.5 rounded-2xl no-underline",
          selected && "bg-grey-25/90",
          className,
        )}
        component={item.isExternalLink ? "a" : "div"}
        href={item.isExternalLink ? item.href : undefined}
        target={item.isExternalLink ? "_blank" : undefined}
        rel={item.isExternalLink ? "noreferrer" : undefined}
        onClick={
          !item.isExternalLink
            ? () => {
                onSelect(item);
                setTooltipOpen(false);
              }
            : undefined
        }
      >
        {item.icon && (
          <NextureIcons
            variant={selected ? "contained" : "outlined"}
            icon={item.icon}
            size={36}
            strokeWidth={1}
            className={cn(
              "transition-transform group-hover:scale-[0.85]",
              (selected || isActive) && "text-primary scale-[0.85]",
            )}
          />
        )}

        <Typography
          variant="body2"
          component="span"
          className={cn(
            "text-text-primary line-clamp-2 w-full text-center font-semibold transition-all",
            (selected || isActive) && "text-primary mt-0 mb-0",
            selected && "text-primary",
          )}
        >
          {t(item.label)}
        </Typography>
      </Box>
    );
  }

  return (
    <Box className={cn("group flex w-full flex-col items-center gap-2", className)}>
      <Tooltip
        key={`left-menu-primary-item-${item.id}`}
        open={tooltipOpen}
        onClose={() => setTooltipOpen(false)}
        onOpen={() => setTooltipOpen(true)}
        title={t(item.label)}
        placement="right"
        arrow
        slotProps={{ tooltip: { className: cn("large", selected && "text-primary") } }}
      >
        <Button
          id={item.id}
          variant="text"
          size="large"
          color={item.color || "text-primary"}
          className={cn(
            "icon-only hover:bg-grey-25/90 text-text-primary h-10 w-10",
            selected &&
              `bg-grey-25/90 active ${item.color ? `text-${item.color.replace("text-", "")}!` : "text-primary!"}`,
            isActive && "active",
          )}
          startIcon={
            item.icon && (
              <NextureIcons
                variant={selected ? "contained" : "outlined"}
                icon={item.icon}
                size={24}
                className={cn(
                  "transition-transform group-hover:scale-[0.85]",
                  (selected || isActive) && "scale-[0.85]",
                )}
              />
            )
          }
          aria-label={t(item.label)}
          {...(item.isExternalLink
            ? {
                component: "a",
                href: item.href,
                target: "_blank",
                rel: "noreferrer",
              }
            : {
                onClick: () => {
                  onSelect(item);
                  setTooltipOpen(false);
                },
              })}
        ></Button>
      </Tooltip>
    </Box>
  );
});
