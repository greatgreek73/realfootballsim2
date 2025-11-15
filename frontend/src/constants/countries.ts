export type CountryOption = {
  code: string;
  label: string;
};

export const COUNTRY_OPTIONS: CountryOption[] = [
  { code: "GB", label: "Great Britain" },
  { code: "ES", label: "Spain" },
  { code: "IT", label: "Italy" },
  { code: "DE", label: "Germany" },
  { code: "FR", label: "France" },
  { code: "PT", label: "Portugal" },
  { code: "GR", label: "Greece" },
  { code: "RU", label: "Russia" },
  { code: "AR", label: "Argentina" },
  { code: "BR", label: "Brazil" },
];

export const COUNTRY_LABELS = COUNTRY_OPTIONS.reduce<Record<string, string>>((acc, option) => {
  acc[option.code] = option.label;
  return acc;
}, {});

export function formatLeagueDisplay(countryCode?: string | null, leagueName?: string | null): string {
  const code = countryCode ?? "";
  const league = leagueName ?? "";
  const countryLabel = code ? COUNTRY_LABELS[code] ?? code : "";

  let base: string;
  if (!league && !countryLabel) {
    base = "—";
  } else if (!league) {
    base = countryLabel;
  } else if (countryLabel && code && league.startsWith(`${code} `)) {
    base = `${countryLabel} ${league.slice(code.length + 1)}`;
  } else if (countryLabel && !league.includes(countryLabel)) {
    base = `${countryLabel} ${league}`;
  } else {
    base = league;
  }

  if (code && !base.includes(`(${code})`)) {
    return `${base} (${code})`;
  }
  return base;
}
