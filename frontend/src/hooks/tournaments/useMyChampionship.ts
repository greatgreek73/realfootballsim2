import { useEffect, useState } from "react";

import { fetchMyChampionship } from "@/api/tournaments";
import { MyChampionshipResponse } from "@/types/tournaments";

export function useMyChampionship() {
  const [data, setData] = useState<MyChampionshipResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchMyChampionship();
        if (!cancelled) {
          setData(result);
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message ?? "Не удалось загрузить ваш чемпионат");
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

