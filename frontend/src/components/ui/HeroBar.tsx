import type { ReactNode } from "react";

type HeroTone = "blue" | "green" | "purple" | "orange" | "teal" | "pink";

interface HeroKpi {
  label: string;
  value: string | number;
  icon?: ReactNode;
  hint?: string;
}

interface HeroBarProps {
  title: string;
  subtitle?: string;
  kpis?: HeroKpi[];
  actions?: ReactNode;
  tone?: HeroTone;
  accent?: ReactNode;
}

const toneClass: Record<HeroTone, string> = {
  blue: "from-blue-700 via-blue-600 to-blue-500",
  green: "from-emerald-600 via-emerald-500 to-lime-500",
  purple: "from-purple-700 via-fuchsia-600 to-violet-500",
  orange: "from-orange-600 via-amber-500 to-yellow-400",
  teal: "from-cyan-700 via-teal-600 to-sky-500",
  pink: "from-rose-600 via-pink-500 to-fuchsia-500",
};

export default function HeroBar({
  title,
  subtitle,
  kpis,
  actions,
  tone = "blue",
  accent,
}: HeroBarProps) {
  return (
    <div className={`text-white rounded-2xl p-5 bg-gradient-to-r ${toneClass[tone]} shadow-lg`}>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col gap-1">
          <div className="text-2xl font-bold">{title}</div>
          {subtitle && <div className="text-sm text-white/85">{subtitle}</div>}
        </div>
        {actions && <div className="flex gap-2 flex-wrap">{actions}</div>}
      </div>

      {accent && <div className="mt-3">{accent}</div>}

      {kpis && kpis.length > 0 && (
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          {kpis.map((kpi, index) => (
            <div key={`${kpi.label}-${index}`} className="bg-white/15 rounded-xl p-3 flex items-start gap-3">
              {kpi.icon && (
                <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                  {kpi.icon}
                </div>
              )}
              <div className="flex flex-col">
                <div className="text-xs uppercase tracking-wide text-white/70">{kpi.label}</div>
                <div className="text-lg font-semibold">{kpi.value}</div>
                {kpi.hint && <div className="text-xs text-white/80 mt-0.5">{kpi.hint}</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
