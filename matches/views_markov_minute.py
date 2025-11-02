from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import random
import yaml
from django.http import JsonResponse

# ---------- helpers ----------
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
    return items[-1]  # на случай округления

def _apply_possession(owner: str, directive: str) -> str:
    if directive == "same":
        return owner
    return "away" if owner == "home" else "home"

def _zone_from_state(state: str) -> str:
    if state in ("OPEN_PLAY_DEF", "GK"):
        return "DEF"
    if state == "OPEN_PLAY_MID":
        return "MID"
    if state == "OPEN_PLAY_FINAL":
        return "FINAL"
    if state == "KICKOFF":
        return "MID"
    return "MID"

# ---------- core minute simulation (MVP) ----------
def _simulate_minute(spec: Dict[str, Any], rng: random.Random,
                     start_state: str = "KICKOFF",
                     start_possession: str = "home") -> Dict[str, Any]:
    states = {s["name"]: s for s in spec.get("states", [])}
    state = start_state
    possession = start_possession
    zone = _zone_from_state(state)

    score = {"home": 0, "away": 0}
    counts = {"shot": 0, "foul": 0, "out": 0, "gk": 0}
    events: List[Dict[str, Any]] = []

    for tick in range(1, 6 + 1):  # 6 тиков = 1 минута
        if state == "SHOT":
            oc = _choose_weighted(rng, states["SHOT"]["outcomes"])
            result = oc.get("result")
            nxt = oc.get("next") or {}
            # фиксируем гол
            if result == "goal":
                counts["shot"] += 1
                if possession == "home":
                    score["home"] += 1
                else:
                    score["away"] += 1
            else:
                counts["shot"] += 1
            # переход после выстрела
            new_state = nxt.get("to")
            possession = _apply_possession(possession, nxt.get("possession", "same"))
            # зона может приехать из next (например, corner: zone FINAL)
            zone = nxt.get("zone", _zone_from_state(new_state))
            events.append({
                "tick": tick, "from": "SHOT", "to": new_state,
                "label": f"SHOT:{result}"
            })
            state = new_state
            continue

        if state == "OUT":
            by_zone = states["OUT"]["by_zone"]
            dist = (by_zone.get(zone) or by_zone["MID"]).get("distribution", [])
            choice = _choose_weighted(rng, dist)
            counts["out"] += 1
            new_state = choice.get("to")
            possession = _apply_possession(possession, choice.get("possession", "same"))
            zone = _zone_from_state(new_state)
            events.append({
                "tick": tick, "from": "OUT", "to": new_state,
                "subtype": choice.get("subtype")
            })
            state = new_state
            continue

        if state == "FOUL":
            by_zone = states["FOUL"]["by_zone"]
            nxt = by_zone.get(zone) or by_zone["MID"]
            counts["foul"] += 1
            new_state = nxt.get("to")
            possession = _apply_possession(possession, nxt.get("possession", "same"))
            zone = _zone_from_state(new_state)
            events.append({"tick": tick, "from": "FOUL", "to": new_state})
            state = new_state
            continue

        if state == "GK":
            tr = states["GK"]["transitions"][0]  # p=1.0
            counts["gk"] += 1
            new_state = tr.get("to")
            possession = _apply_possession(possession, tr.get("possession", "same"))
            zone = _zone_from_state(new_state)
            events.append({"tick": tick, "from": "GK", "to": new_state})
            state = new_state
            continue

        # OPEN_PLAY_* и KICKOFF идут по transitions
        tr = _choose_weighted(rng, states[state]["transitions"])
        new_state = tr.get("to")
        possession = _apply_possession(possession, tr.get("possession", "same"))
        # зона из перехода (если есть) или из нового состояния
        zone = tr.get("zone", _zone_from_state(new_state))
        label = None
        if new_state == "SHOT":
            label = "→SHOT"
        elif new_state == "OUT":
            label = "→OUT"
        elif new_state == "FOUL":
            label = "→FOUL"
        elif new_state == "GK":
            label = "→GK"
        events.append({
            "tick": tick, "from": state, "to": new_state,
            "p": tr.get("p"), "zone": zone, "possession": possession, "label": label
        })
        state = new_state

    return {
        "start_state": start_state,
        "end_state": state,
        "possession_end": possession,
        "score": score,
        "counts": counts,
        "events": events,
    }

# ---------- Django view ----------
def markov_minute(request):
    """
    Возвращает сводку за одну минуту (6 тиков) по YAML-спеке.
    Параметры: ?seed=<int> (по умолчанию 73)
    """
    spec = _load_spec()
    seed_value = int(request.GET.get("seed", "73"))
    rng = random.Random(seed_value)
    minute_summary = _simulate_minute(spec, rng, start_state="KICKOFF", start_possession="home")
    result = {
        "spec_version": spec.get("version"),
        "tick_seconds": spec["time"]["tick_seconds"],
        "seed": seed_value,
        "minute_summary": minute_summary,
    }
    return JsonResponse(result)
