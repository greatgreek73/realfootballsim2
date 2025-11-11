from __future__ import annotations

import json
from typing import Any, Dict, Optional

from django.http import JsonResponse

from matches.engines.markov_runtime import simulate_markov_minute


def _clean_override(params: Dict[str, Optional[str]]) -> Optional[Dict[str, Any]]:
    cleaned: Dict[str, Any] = {}
    for key, value in params.items():
        if value is None or value == "":
            continue
        cleaned[key] = value
    return cleaned or None


def markov_minute(request):
    """
    Lightweight proxy around the reusable Markov runtime.

    Query parameters:
      - seed: int (defaults to 73)
      - token: JSON blob produced by the previous response (optional)
      - home / away: display names (optional)
      - attack_home / attack_away / defense_home / defense_away: coefficient overrides
    """
    seed_value = int(request.GET.get("seed", "73"))
    home_name = request.GET.get("home") or "Home"
    away_name = request.GET.get("away") or "Away"

    token_data: Optional[dict] = None
    token_raw = request.GET.get("token")
    if token_raw:
        try:
            token_data = json.loads(token_raw)
        except json.JSONDecodeError:
            token_data = None

    attack_override = _clean_override(
        {"home": request.GET.get("attack_home"), "away": request.GET.get("attack_away")}
    )
    defense_override = _clean_override(
        {"home": request.GET.get("defense_home"), "away": request.GET.get("defense_away")}
    )

    result = simulate_markov_minute(
        seed=seed_value,
        token=token_data,
        home_name=home_name,
        away_name=away_name,
        attack_override=attack_override,
        defense_override=defense_override,
    )

    resp = JsonResponse(result)
    origin = request.headers.get("Origin")
    if origin in ("http://127.0.0.1:5173", "http://localhost:5173"):
        resp["Access-Control-Allow-Origin"] = origin
        resp["Vary"] = "Origin"
    return resp
