import { OpenedAccordion } from "./left-menu";
import { Dispatch, useCallback, useEffect, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Link, useLocation } from "react-router-dom";

import { Accordion, AccordionDetails, AccordionSummary, Button } from "@mui/material";

import NiChevronRightSmall from "@/icons/nexture/ni-chevron-right-small";
import NextureIcons from "@/icons/nexture-icons";
import { cn, isPathMatch } from "@/lib/utils";
import { MenuItem } from "@/types/types";

type Props = {
  item: MenuItem;
  indent: number;
  openedAccordions: OpenedAccordion[];
  setOpenedAccordions: Dispatch<React.SetStateAction<OpenedAccordion[]>>;
  className?: string;
};

export function SecondaryItem({ item, indent = 0, openedAccordions, setOpenedAccordions, className }: Props) {
  const { t } = useTranslation();
  const { pathname } = useLocation();

  const isActive = useMemo(() => {
    if (item.href && isPathMatch(pathname, item.href)) return true;
    if (item.children) return item.children.some((child) => child.href && isPathMatch(pathname, child.href));
    return false;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  const handleOnChange = useCallback(
    (expanded: boolean) => {
      if (expanded) {
        setOpenedAccordions([...openedAccordions.filter((a) => a.indent !== indent), { indent, id: item.id }]);
      } else {
        setOpenedAccordions(openedAccordions.filter((a) => a.indent !== indent && a.id !== item.id));
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [openedAccordions],
  );

  useEffect(() => {
    if (isActive) {
      setOpenedAccordions((prev) => [...prev.filter((a) => a.indent !== indent), { indent, id: item.id }]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive]);

  if (item.isExternalLink) {
    return (
      <Button
        variant="text"
        size={indent === 0 ? "large" : "medium"}
        color="text-primary"
        className={cn(
          "full-width-button group hover:bg-grey-25 px-4",
          isActive && "active text-primary! bg-grey-25!",
          className,
        )}
        component="a"
        href={item.href}
        target="_blank"
        startIcon={
          item.icon && (
            <NextureIcons
              variant={isActive ? "contained" : "outlined"}
              icon={item.icon}
              size={indent === 0 ? "large" : "medium"}
              className={cn("transition-transform group-hover:scale-[0.85]", isActive && "scale-[0.85]")}
            />
          )
        }
        aria-label={t(item.label)}
        rel="noreferrer"
      >
        {t(item.label)}
      </Button>
    );
  }

  // the item is a link without children
  if ((!item.children || item.children.filter((x) => !x.hideInMenu).length === 0) && item.href) {
    return (
      <Button
        variant="text"
        size={indent === 0 ? "large" : "medium"}
        color="text-primary"
        className={cn(
          "full-width-button group hover:bg-grey-25 px-4",
          isActive && "active text-primary! bg-grey-25!",
          className,
        )}
        startIcon={
          item.icon && (
            <NextureIcons
              variant={isActive ? "contained" : "outlined"}
              icon={item.icon}
              size={indent === 0 ? "large" : "medium"}
              className={cn("transition-transform group-hover:scale-[0.85]", isActive && "scale-[0.85]")}
            />
          )
        }
        aria-label={t(item.label)}
        component={Link}
        to={item.href}
      >
        {t(item.label)}
      </Button>
    );
  }

  // Item has children - render as accordion
  const isExpanded = !!openedAccordions.find((a) => a.id === item.id && a.indent === indent);

  return (
    <Accordion expanded={isExpanded} onChange={(_, expanded) => handleOnChange(expanded)}>
      <AccordionSummary>
        <Button
          variant="text"
          size={indent === 0 ? "large" : "medium"}
          color="text-primary"
          className={cn(
            "full-width-button group hover:bg-grey-25 px-4",
            isActive && "text-primary! bg-grey-25!",
            (isExpanded || isActive) && "active",
            className,
          )}
          startIcon={
            item.icon && (
              <NextureIcons
                variant={isActive ? "contained" : "outlined"}
                icon={item.icon}
                size={indent === 0 ? "large" : "medium"}
                className={cn(
                  "transition-transform group-hover:scale-[0.85]",
                  (isActive || isExpanded) && "scale-[0.85]",
                )}
              />
            )
          }
          endIcon={<NiChevronRightSmall size="medium" className="accordion-rotate" />}
          component="div"
        >
          {t(item.label)}
        </Button>
      </AccordionSummary>
      <AccordionDetails className="ml-7 flex flex-col gap-1 pt-2">
        {item.children?.map((child) => (
          <SecondaryItem
            className={className}
            item={child}
            key={`left-menu-secondary-item-${item.id}-${child.id}`}
            indent={indent + 1}
            openedAccordions={openedAccordions}
            setOpenedAccordions={setOpenedAccordions}
          />
        ))}
      </AccordionDetails>
    </Accordion>
  );
}
