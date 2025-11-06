import { useEffect, useState } from "react";

import { fetchLeagues } from "@/api/tournaments";
import { LeagueSummary } from "@/types/tournaments";

export interface UseLeaguesParams {
  country?: string;
  level?: number;
}

export function useLeagues(filters: UseLeaguesParams = {}) {
  const [data, setData] = useState<LeagueSummary[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchLeagues({
          ...(filters.country ? { country: filters.country } : {}),
          ...(filters.level ? { level: filters.level } : {}),
        });
        if (!cancelled) {
          setData(result);
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message ?? "Не удалось загрузить лиги");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [filters.country, filters.level]);

  return { data, loading, error };
}

