import { useEffect, useState } from "react";

import { fetchChampionshipDetail, fetchChampionshipMatches } from "@/api/tournaments";
import {
  ChampionshipDetailResponse,
  ChampionshipMatchSummary,
} from "@/types/tournaments";

export function useChampionshipDetail(championshipId: number | null) {
  const [detail, setDetail] = useState<ChampionshipDetailResponse | null>(null);
  const [matches, setMatches] = useState<ChampionshipMatchSummary[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!championshipId) {
      setDetail(null);
      setMatches(null);
      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [detailResponse, matchesResponse] = await Promise.all([
          fetchChampionshipDetail(championshipId),
          fetchChampionshipMatches(championshipId),
        ]);

        if (!cancelled) {
          setDetail(detailResponse);
          setMatches(matchesResponse.matches);
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message ?? "Не удалось загрузить данные чемпионата");
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
  }, [championshipId]);

  return { detail, matches, loading, error };
}

