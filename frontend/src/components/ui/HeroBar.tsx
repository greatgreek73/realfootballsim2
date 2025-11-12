import { Children, type ReactNode } from "react";

type HeroTone = "blue" | "green" | "purple" | "orange" | "teal" | "pink";

type HeroKpiBadgeTone = "success" | "warning" | "danger";

interface HeroKpi {
  label: string;
  value: string | number;
  icon?: ReactNode;
  hint?: ReactNode;
  badge?: {
    label: string;
    tone?: HeroKpiBadgeTone;
  };
  tooltip?: string;
}

interface HeroBarProps {
  title: string;
  subtitle?: string;
  kpis?: HeroKpi[];
  actions?: ReactNode;
  tone?: HeroTone;
}

const toneClass: Record<HeroTone, string> = {
  blue: "from-blue-700 via-blue-600 to-blue-500",
  green: "from-emerald-600 via-emerald-500 to-lime-500",
  purple: "from-purple-700 via-fuchsia-600 to-violet-500",
  orange: "from-orange-600 via-amber-500 to-yellow-400",
  teal: "from-cyan-700 via-teal-600 to-sky-500",
  pink: "from-rose-600 via-pink-500 to-fuchsia-500",
};

const badgeToneClass: Record<HeroKpiBadgeTone, string> = {
  success: "bg-emerald-400/90 text-emerald-950",
  warning: "bg-amber-300/90 text-amber-900",
  danger: "bg-rose-500/90 text-white",
};

export default function HeroBar({ title, subtitle, kpis, actions, tone = "blue" }: HeroBarProps) {
  const safeKpis = (kpis ?? []).slice(0, 4);
  const actionNodes = Children.toArray(actions).slice(0, 2);

  return (
    <div className={`text-white rounded-2xl p-5 bg-gradient-to-r ${toneClass[tone]} shadow-lg`}>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col gap-1">
          <div className="text-2xl font-bold">{title}</div>
          {subtitle && <div className="text-sm text-white/85">{subtitle}</div>}
        </div>
        {actionNodes.length > 0 && (
          <div className="flex flex-row flex-wrap justify-start gap-2 lg:justify-end">
            {actionNodes.map((node, index) => (
              <div key={index}>{node}</div>
            ))}
          </div>
        )}
      </div>

      {safeKpis.length > 0 && (
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {safeKpis.map((kpi, index) => (
            <div
              key={`${kpi.label}-${index}`}
              className="bg-white/15 rounded-xl p-4 flex gap-3"
              title={kpi.tooltip}
            >
              {kpi.icon && (
                <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                  {kpi.icon}
                </div>
              )}
              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-2">
                  <div className="text-xs uppercase tracking-wide text-white/70">{kpi.label}</div>
                  {kpi.badge && (
                    <span
                      className={`text-[10px] font-semibold uppercase tracking-wide rounded-full px-2 py-0.5 leading-none ${badgeToneClass[kpi.badge.tone ?? "success"]}`}
                    >
                      {kpi.badge.label}
                    </span>
                  )}
                </div>
                <div className="text-lg font-semibold leading-tight">{kpi.value}</div>
                {kpi.hint && <div className="text-xs text-white/80 mt-0.5">{kpi.hint}</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
