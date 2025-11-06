import { useEffect, useState } from "react";

import { fetchSeasons } from "@/api/tournaments";
import { SeasonSummary } from "@/types/tournaments";

export function useSeasons() {
  const [data, setData] = useState<SeasonSummary[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchSeasons();
        if (!cancelled) {
          setData(result);
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message ?? "Не удалось загрузить сезоны");
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
  }, []);

  return { data, loading, error };
}

