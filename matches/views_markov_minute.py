from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json
import hashlib
import random
import yaml
from django.http import JsonResponse

def _load_spec() -> Dict[str, Any]:
    spec_path = Path(__file__).resolve().parent / "engines" / "markov_spec_v0.yaml"
    return yaml.safe_load(spec_path.read_text(encoding="utf-8"))

def _choose_weighted(rng: random.Random, items: List[dict]) -> dict:
    r = rng.random()
    acc = 0.0
    for item in items:
        acc += float(item.get("p", 0.0))
        if r <= acc:
            return item
    return items[-1]  # на случай округлений

def _apply_possession(owner: str, directive: str) -> str:
    return owner if directive == "same" else ("away" if owner == "home" else "home")

def _zone_from_state(state: str) -> str:
    if state in ("OPEN_PLAY_DEF", "GK"):
        return "DEF"
    if state == "OPEN_PLAY_MID" or state == "KICKOFF":
        return "MID"
    if state == "OPEN_PLAY_FINAL":
        return "FINAL"
    return "MID"

def _rng_from(seed: int, start_state: str, start_possession: str, start_zone: str) -> random.Random:
    """Детерминированный RNG на основе seed + стартового контекста."""
    key = f"{seed}|{start_state}|{start_possession}|{start_zone}"
    h = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
    return random.Random(h)

def _simulate_minute(
    spec: Dict[str, Any],
    rng: random.Random,
    *,
    start_state: str = "KICKOFF",
    start_possession: str = "home",
    start_zone: str | None = None,
) -> Dict[str, Any]:
    states = {s["name"]: s for s in spec.get("states", [])}
    state = start_state
    possession = start_possession
    zone = start_zone or _zone_from_state(state)

    score = {"home": 0, "away": 0}
    counts = {"shot": 0, "foul": 0, "out": 0, "gk": 0}
    possession_ticks = {"home": 0, "away": 0}
    entries_final = {"home": 0, "away": 0}
    events: List[Dict[str, Any]] = []

    for tick in range(1, 6 + 1):  # 6 тиков = 1 минута
        possession_ticks[possession] += 1

        if state == "SHOT":
            oc = _choose_weighted(rng, states["SHOT"]["outcomes"])
            result = oc.get("result")
            nxt = oc.get("next") or {}
            counts["shot"] += 1
            if result == "goal":
                score[possession] += 1
            new_state = nxt.get("to")
            new_pos = _apply_possession(possession, nxt.get("possession", "same"))
            new_zone = nxt.get("zone", _zone_from_state(new_state))
            events.append({"tick": tick, "from": "SHOT", "to": new_state, "label": f"SHOT:{result}"})
            if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
                entries_final[new_pos] += 1
            state, possession, zone = new_state, new_pos, new_zone
            continue

        if state == "OUT":
            by_zone = states["OUT"]["by_zone"]
            dist = (by_zone.get(zone) or by_zone["MID"]).get("distribution", [])
            choice = _choose_weighted(rng, dist)
            counts["out"] += 1
            new_state = choice.get("to")
            new_pos = _apply_possession(possession, choice.get("possession", "same"))
            new_zone = _zone_from_state(new_state)
            events.append({
                "tick": tick, "from": "OUT", "to": new_state, "subtype": choice.get("subtype")
            })
            if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
                entries_final[new_pos] += 1
            state, possession, zone = new_state, new_pos, new_zone
            continue

        if state == "FOUL":
            by_zone = states["FOUL"]["by_zone"]
            nxt = by_zone.get(zone) or by_zone["MID"]
            counts["foul"] += 1
            new_state = nxt.get("to")
            new_pos = _apply_possession(possession, nxt.get("possession", "same"))
            new_zone = _zone_from_state(new_state)
            events.append({"tick": tick, "from": "FOUL", "to": new_state})
            if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
                entries_final[new_pos] += 1
            state, possession, zone = new_state, new_pos, new_zone
            continue

        if state == "GK":
            tr = states["GK"]["transitions"][0]  # p=1.0
            counts["gk"] += 1
            new_state = tr.get("to")
            new_pos = _apply_possession(possession, tr.get("possession", "same"))
            new_zone = _zone_from_state(new_state)
            events.append({"tick": tick, "from": "GK", "to": new_state})
            if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
                entries_final[new_pos] += 1
            state, possession, zone = new_state, new_pos, new_zone
            continue

        # OPEN_PLAY_* и KICKOFF
        tr = _choose_weighted(rng, states[state]["transitions"])
        new_state = tr.get("to")
        new_pos = _apply_possession(possession, tr.get("possession", "same"))
        new_zone = tr.get("zone", _zone_from_state(new_state))
        label = None
        if new_state in ("SHOT", "OUT", "FOUL", "GK"):
            label = f"→{new_state}"
        events.append({
            "tick": tick, "from": state, "to": new_state,
            "p": tr.get("p"), "zone": new_zone, "possession": new_pos, "label": label
        })
        if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
            entries_final[new_pos] += 1
        state, possession, zone = new_state, new_pos, new_zone

    possession_pct = {
        "home": round(100.0 * possession_ticks["home"] / 6.0, 1),
        "away": round(100.0 * possession_ticks["away"] / 6.0, 1),
    }

    return {
        "start_state": start_state,
        "end_state": state,
        "possession_end": possession,
        "zone_end": zone,
        "score": score,
        "counts": counts,
        "events": events,
        "possession_pct": possession_pct,
        "entries_final_third": entries_final,
        "token": {"state": state, "possession": possession, "zone": zone},
    }

def markov_minute(request):
    """
    Возвращает сводку за одну минуту (6 тиков) по YAML-спеке.
    Параметры:
      - seed: int (по умолчанию 73)
      - token: JSON-строка {"state": "...", "possession": "home|away", "zone": "DEF|MID|FINAL"}
    """
    spec = _load_spec()
    seed_value = int(request.GET.get("seed", "73"))
    # начальные условия
    start_state = "KICKOFF"
    start_pos = "home"
    start_zone = _zone_from_state(start_state)

    token_param = request.GET.get("token")
    if token_param:
        try:
            t = json.loads(token_param)
            start_state = t.get("state", start_state)
            start_pos = t.get("possession", start_pos)
            start_zone = t.get("zone", start_zone)
        except Exception:
            pass  # игнорируем битый token

    rng = _rng_from(seed_value, start_state, start_pos, start_zone)
    minute_summary = _simulate_minute(
        spec, rng, start_state=start_state, start_possession=start_pos, start_zone=start_zone
    )

    result = {
        "spec_version": spec.get("version"),
        "tick_seconds": spec["time"]["tick_seconds"],
        "seed": seed_value,
        "minute_summary": minute_summary,
    }
    # Локальный CORS для dev (Vite 5173)
    resp = JsonResponse(result)
    origin = request.headers.get("Origin")
    if origin in ("http://127.0.0.1:5173", "http://localhost:5173"):
        resp["Access-Control-Allow-Origin"] = origin
        resp["Vary"] = "Origin"
    return resp
