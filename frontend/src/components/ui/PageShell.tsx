import type { ReactNode } from "react";

type BottomSplit = "67-33" | "50-50";

interface PageShellProps {
  hero?: ReactNode;
  header?: ReactNode;
  top?: ReactNode;
  main: ReactNode;
  aside?: ReactNode;
  footer?: ReactNode;
  bottomSplit?: BottomSplit;
}

/**
 * Универсальный каркас: верхние блоки на всю ширину + две нижние колонки.
 * По умолчанию низ делится как 2/3 (main) и 1/3 (aside). Для страниц,
 * где нужен паритет (например, сравнение игроков), можно включить 50/50.
 */
export default function PageShell({
  hero,
  header,
  top,
  main,
  aside,
  footer,
  bottomSplit = "67-33",
}: PageShellProps) {
  const hasAside = Boolean(aside);
  const bottomGridCols =
    bottomSplit === "50-50" ? "xl:grid-cols-2" : "xl:grid-cols-[2fr_1fr]";
  const gridClass = hasAside
    ? `grid grid-cols-1 ${bottomGridCols} gap-4`
    : "grid grid-cols-1 gap-4";

  return (
    <div className="flex min-h-full flex-1 flex-col gap-4">
      {hero && <div>{hero}</div>}
      {header && <div>{header}</div>}
      {top && <div>{top}</div>}

      <div className={`${gridClass} flex-1 min-h-0`}>
        <div className="flex h-full flex-1 flex-col min-h-0">{main}</div>
        {aside && <div className="flex h-full flex-1 flex-col min-h-0">{aside}</div>}
      </div>

      {footer && <div>{footer}</div>}
    </div>
  );
}
