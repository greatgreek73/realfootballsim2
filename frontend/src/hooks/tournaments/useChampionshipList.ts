import { useEffect, useState } from "react";

import { fetchChampionships } from "@/api/tournaments";
import { ChampionshipSummary } from "@/types/tournaments";

export interface UseChampionshipListParams {
  seasonId?: number;
  leagueId?: number;
  country?: string;
  status?: string;
}

export function useChampionshipList(filters: UseChampionshipListParams = {}) {
  const [data, setData] = useState<ChampionshipSummary[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchChampionships({
          ...(filters.seasonId ? { season_id: filters.seasonId } : {}),
          ...(filters.leagueId ? { league_id: filters.leagueId } : {}),
          ...(filters.country ? { country: filters.country } : {}),
          ...(filters.status ? { status: filters.status } : {}),
        });

        if (!cancelled) {
          setData(result);
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message ?? "Не удалось загрузить чемпионаты");
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
  }, [filters.seasonId, filters.leagueId, filters.country, filters.status]);

  return { data, loading, error };
}

