from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json
import hashlib
import random

import yaml
from django.http import JsonResponse

TICKS_PER_MINUTE = 6

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
    return items[-1] if items else {}

def _apply_possession(owner: str, directive: str) -> str:
    return owner if directive == "same" else ("away" if owner == "home" else "home")

def _zone_from_state(state: str) -> str:
    if state in ("OPEN_PLAY_DEF", "GK"):
        return "DEF"
    if state in ("OPEN_PLAY_MID", "KICKOFF"):
        return "MID"
    if state == "OPEN_PLAY_FINAL":
        return "FINAL"
    return "MID"

def _rng_from(seed: int, minute_index: int, start_state: str, start_possession: str, start_zone: str) -> random.Random:
    key = f"{seed}|m={minute_index}|{start_state}|{start_possession}|{start_zone}"
    h = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
    return random.Random(h)


def _adjust_advancing_transitions(
    transitions: List[dict],
    *,
    state: str,
    possession: str,
    attack_coeffs: Dict[str, float],
    defense_coeffs: Dict[str, float],
) -> List[dict]:
    if state not in ("OPEN_PLAY_MID", "OPEN_PLAY_FINAL"):
        return transitions

    adjusted: List[dict] = []
    weights: List[float] = []
    total = 0.0

    for tr in transitions:
        base_p = float(tr.get("p", 0.0))
        if base_p <= 0.0:
            continue

        multiplier = 1.0
        to_state = tr.get("to")
        possession_directive = tr.get("possession", "same")
        advancing = (
            state == "OPEN_PLAY_MID"
            and to_state == "OPEN_PLAY_FINAL"
            and possession_directive == "same"
        ) or (
            state == "OPEN_PLAY_FINAL"
            and to_state == "SHOT"
            and possession_directive == "same"
        )

        if advancing and possession in ("home", "away"):
            team = possession
            opponent = "away" if team == "home" else "home"
            attack = attack_coeffs.get(team, 1.0)
            defense = defense_coeffs.get(opponent, 1.0)
            multiplier *= max(attack, 0.01)
            multiplier /= max(defense, 0.01)

        new_p = base_p * multiplier
        adjusted.append(tr)
        weights.append(new_p)
        total += new_p

    if total <= 0.0:
        return transitions

    normalized: List[dict] = []
    for tr, new_p in zip(adjusted, weights):
        tr_copy = dict(tr)
        tr_copy["p"] = new_p / total
        normalized.append(tr_copy)
    return normalized

# -------------------- Narrative helpers --------------------

def _side_name(side: str | None, home_name: str, away_name: str) -> str:
    if side == "home":
        return home_name
    if side == "away":
        return away_name
    return "-"

def _zone_label(z: str | None) -> str:
    return {"DEF": "defensive third", "MID": "midfield", "FINAL": "final third"}.get(z or "", "midfield")

def _event_phrase(e: dict, home_name: str, away_name: str) -> str | None:
    frm = str(e.get("from", ""))
    to = str(e.get("to", ""))
    label = e.get("label")
    subtype = e.get("subtype")
    pos = e.get("possession")
    zone = e.get("zone")
    who = _side_name(pos, home_name, away_name)
    z = _zone_label(zone)
    turnover = bool(e.get("turnover"))

    # OPEN_PLAY → OPEN_PLAY
    if frm.startswith("OPEN_PLAY_") and to.startswith("OPEN_PLAY_"):
        # смена владения — проговариваем явно
        if turnover:
            if to == "OPEN_PLAY_DEF":
                return f"Turnover! {who} win the ball and drop into defensive third"
            if to == "OPEN_PLAY_MID":
                return f"Turnover! {who} win the ball in midfield"
            if to == "OPEN_PLAY_FINAL":
                return f"Turnover! {who} win the ball in the final third"
            return f"Turnover! {who} win the ball"

        # без перехвата — позиционные формулировки
        if label in ("→FOUL", "→OUT", "→SHOT"):
            return None
        if frm == "OPEN_PLAY_DEF" and to == "OPEN_PLAY_MID":
            return f"{who} build from the back into midfield"
        if frm == "OPEN_PLAY_MID" and to == "OPEN_PLAY_FINAL":
            return f"{who} advance into the final third"
        if frm == "OPEN_PLAY_FINAL" and to == "OPEN_PLAY_MID":
            return f"{who} recycle possession back to midfield"
        return f"{who} keep possession in {z}"

    # OUT
    if frm == "OUT":
        if subtype == "throw_in":
            return f"Throw-in for {who} in {z}"
        if subtype == "corner":
            return f"Corner to {who}"
        if subtype == "goal_kick":
            return f"Goal kick for {who}"
        return f"Restart for {who} in {z}"

    # FOUL
    if frm == "FOUL":
        return f"Foul. {who} restart in {z}"

    # GK
    if frm == "GK":
        return f"Goalkeeper restart for {who}"

    # SHOT
    if frm == "SHOT":
        res = str(label or "")
        if res.startswith("SHOT:"):
            res = res.split(":", 1)[1]
        if res == "goal":
            return f"GOAL! {who} score."
        if res == "saved":
            return f"Shot saved — {who} keep the ball"
        if res == "off_target":
            return f"Shot off target — {who} with the goal kick"
        if res == "deflected_corner":
            return f"Shot deflected — corner to {who}"
        return f"Shot — outcome: {res}" if res else "Shot"

    return None

# -------------------- append events consistently --------------------
def _push_event(
    events: List[Dict[str, Any]],
    *,
    tick: int,
    frm: str,
    to: str,
    new_pos: str,
    new_zone: str,
    prev_pos: str,
    label: str | None = None,
    subtype: str | None = None,
    p: float | None = None,
) -> None:
    ev: Dict[str, Any] = {
        "tick": tick,
        "from": frm,
        "to": to,
        "possession": new_pos,
        "zone": new_zone,
        "prev_possession": prev_pos,
        "turnover": (prev_pos is not None and new_pos is not None and new_pos != prev_pos),
    }
    if label is not None:
        ev["label"] = label
    if subtype is not None:
        ev["subtype"] = subtype
    if p is not None:
        ev["p"] = p
    events.append(ev)

# -----------------------------------------------------------

def _simulate_minute(
    spec: Dict[str, Any],
    rng: random.Random,
    *,
    start_state: str = "KICKOFF",
    start_possession: str = "home",
    start_zone: str | None = None,
    attack_coeffs: Dict[str, float] | None = None,
    defense_coeffs: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    if attack_coeffs is None:
        attack_coeffs = {"home": 1.0, "away": 1.0}
    if defense_coeffs is None:
        defense_coeffs = {"home": 1.0, "away": 1.0}

    states = {s["name"]: s for s in spec.get("states", [])}
    state = start_state
    possession = start_possession
    zone = start_zone or _zone_from_state(state)

    score = {"home": 0, "away": 0}
    counts = {"shot": 0, "foul": 0, "out": 0, "gk": 0}
    possession_ticks = {"home": 0, "away": 0}
    entries_final = {"home": 0, "away": 0}
    events: List[Dict[str, Any]] = []

    for tick in range(1, TICKS_PER_MINUTE + 1):
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
            _push_event(
                events, tick=tick, frm="SHOT", to=new_state,
                new_pos=new_pos, new_zone=new_zone, prev_pos=possession,
                label=f"SHOT:{result}"
            )
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
            _push_event(
                events, tick=tick, frm="OUT", to=new_state,
                new_pos=new_pos, new_zone=new_zone, prev_pos=possession,
                subtype=choice.get("subtype")
            )
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
            _push_event(
                events, tick=tick, frm="FOUL", to=new_state,
                new_pos=new_pos, new_zone=new_zone, prev_pos=possession
            )
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
            _push_event(
                events, tick=tick, frm="GK", to=new_state,
                new_pos=new_pos, new_zone=new_zone, prev_pos=possession
            )
            if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
                entries_final[new_pos] += 1
            state, possession, zone = new_state, new_pos, new_zone
            continue

        # обычные переходы из OPEN_PLAY_*
        transitions = states[state]["transitions"]
        transitions = _adjust_advancing_transitions(
            transitions,
            state=state,
            possession=possession,
            attack_coeffs=attack_coeffs,
            defense_coeffs=defense_coeffs,
        )
        tr = _choose_weighted(rng, transitions)
        new_state = tr.get("to")
        new_pos = _apply_possession(possession, tr.get("possession", "same"))
        new_zone = tr.get("zone", _zone_from_state(new_state))
        label = None
        if new_state in ("SHOT", "OUT", "FOUL", "GK"):
            label = f"→{new_state}"
        _push_event(
            events, tick=tick, frm=state, to=new_state,
            new_pos=new_pos, new_zone=new_zone, prev_pos=possession,
            label=label, p=tr.get("p")
        )
        if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
            entries_final[new_pos] += 1
        state, possession, zone = new_state, new_pos, new_zone

    # время на тик возьмем из спеки
    tick_seconds = int(spec.get("time", {}).get("tick_seconds", 10))

    possession_pct = {
        "home": round(100.0 * possession_ticks["home"] / float(TICKS_PER_MINUTE), 1),
        "away": round(100.0 * possession_ticks["away"] / float(TICKS_PER_MINUTE), 1),
    }
    possession_seconds = {
        "home": possession_ticks["home"] * tick_seconds,
        "away": possession_ticks["away"] * tick_seconds,
    }
    possession_swings = sum(1 for e in events if e.get("turnover"))

    expected_seconds_total = TICKS_PER_MINUTE * tick_seconds
    actual_seconds_total = possession_seconds["home"] + possession_seconds["away"]
    pct_from_seconds_home = round(100.0 * possession_seconds["home"] / float(expected_seconds_total), 1)
    pct_from_seconds_away = round(100.0 * possession_seconds["away"] / float(expected_seconds_total), 1)
    pct_diff_home = abs(pct_from_seconds_home - possession_pct["home"])
    pct_diff_away = abs(pct_from_seconds_away - possession_pct["away"])
    swings_expected = sum(1 for e in events if e.get("turnover"))

    entries_recount = {"home": 0, "away": 0}
    prev_state_for_entry = start_state
    prev_pos_for_entry = start_possession
    for ev in events:
        to_state = ev.get("to")
        new_pos = ev.get("possession")
        if (
            to_state == "OPEN_PLAY_FINAL"
            and prev_state_for_entry != "OPEN_PLAY_FINAL"
            and new_pos in entries_recount
        ):
            entries_recount[new_pos] += 1
        prev_state_for_entry = to_state
        prev_pos_for_entry = new_pos

    validation = {
        "seconds_total": {
            "expected": expected_seconds_total,
            "actual": actual_seconds_total,
            "ok": actual_seconds_total == expected_seconds_total,
        },
        "possession_pct": {
            "home_diff": pct_diff_home,
            "away_diff": pct_diff_away,
            "ok": pct_diff_home <= 0.1 and pct_diff_away <= 0.1,
        },
        "swings": {
            "expected": swings_expected,
            "actual": possession_swings,
            "ok": swings_expected == possession_swings,
        },
        "entries_final_third": {
            "home": {
                "expected": entries_recount["home"],
                "actual": entries_final.get("home", 0),
                "ok": entries_recount["home"] == entries_final.get("home", 0),
            },
            "away": {
                "expected": entries_recount["away"],
                "actual": entries_final.get("away", 0),
                "ok": entries_recount["away"] == entries_final.get("away", 0),
            },
        },
    }

    return {
        "start_state": start_state,
        "end_state": state,
        "possession_end": possession,
        "zone_end": zone,
        "score": score,  # дельта за минуту
        "counts": counts,
        "events": events,
        "possession_pct": possession_pct,
        "possession_seconds": possession_seconds,
        "possession_swings": possession_swings,
        "entries_final_third": entries_final,
        "validation": validation,
    }

def markov_minute(request):
    """
    1 "минутка" = 6 тиков.
    GET:
      - seed: int (по умолчанию 73)
      - token: JSON {"state","possession","zone","minute","total_score"}
      - home: название хозяев (опционально)
      - away: название гостей (опционально)
    """
    spec = _load_spec()
    seed_value = int(request.GET.get("seed", "73"))

    # имена команд для Narrative (если не передали — используем простые метки)
    home_name = request.GET.get("home") or "Home"
    away_name = request.GET.get("away") or "Away"

    # начальные условия
    start_state = "KICKOFF"
    start_pos = "home"
    start_zone = _zone_from_state(start_state)
    minute_index = 1
    total_score = {"home": 0, "away": 0}
    coefficients = {
        "attack": {"home": 1.0, "away": 1.0},
        "defense": {"home": 1.0, "away": 1.0},
    }

    def _parse_coeff(value: str | None, default: float) -> float:
        if value is None:
            return default
        try:
            parsed = float(value)
            if not (parsed > 0.0 and parsed < 10.0):
                return default
            return parsed
        except Exception:
            return default

    token_param = request.GET.get("token")
    if token_param:
        try:
            t = json.loads(token_param)
            start_state = t.get("state", start_state)
            start_pos = t.get("possession", start_pos)
            start_zone = t.get("zone", start_zone)
            minute_index = int(t.get("minute", minute_index))
            ts = t.get("total_score")
            if isinstance(ts, dict):
                total_score["home"] = int(ts.get("home", 0))
                total_score["away"] = int(ts.get("away", 0))
            coeff_token = t.get("coefficients")
            if isinstance(coeff_token, dict):
                attack_token = coeff_token.get("attack")
                defense_token = coeff_token.get("defense")
                if isinstance(attack_token, dict):
                    coefficients["attack"]["home"] = _parse_coeff(attack_token.get("home"), coefficients["attack"]["home"])
                    coefficients["attack"]["away"] = _parse_coeff(attack_token.get("away"), coefficients["attack"]["away"])
                if isinstance(defense_token, dict):
                    coefficients["defense"]["home"] = _parse_coeff(defense_token.get("home"), coefficients["defense"]["home"])
                    coefficients["defense"]["away"] = _parse_coeff(defense_token.get("away"), coefficients["defense"]["away"])
        except Exception:
            pass

    coefficients["attack"]["home"] = _parse_coeff(request.GET.get("attack_home"), coefficients["attack"]["home"])
    coefficients["attack"]["away"] = _parse_coeff(request.GET.get("attack_away"), coefficients["attack"]["away"])
    coefficients["defense"]["home"] = _parse_coeff(request.GET.get("defense_home"), coefficients["defense"]["home"])
    coefficients["defense"]["away"] = _parse_coeff(request.GET.get("defense_away"), coefficients["defense"]["away"])

    rng = _rng_from(seed_value, minute_index, start_state, start_pos, start_zone)
    minute_summary = _simulate_minute(
        spec,
        rng,
        start_state=start_state,
        start_possession=start_pos,
        start_zone=start_zone,
        attack_coeffs=coefficients["attack"],
        defense_coeffs=coefficients["defense"],
    )

    # накопительный счёт
    new_total = {
        "home": total_score["home"] + minute_summary["score"]["home"],
        "away": total_score["away"] + minute_summary["score"]["away"],
    }

    # Narrative (server‑side)
    narrative: List[str] = []

    # Kick-off lines
    if minute_index == 1 and start_state == "KICKOFF":
        narrative.append(f"Kick-off by {_side_name(start_pos, home_name, away_name)}")
    elif minute_index == 46 and start_state == "KICKOFF":
        narrative.append(f"Second-half kick-off by {_side_name(start_pos, home_name, away_name)}")

    for e in minute_summary.get("events", []):
        text = _event_phrase(e, home_name, away_name)
        if text:
            narrative.append(text)
    if not narrative:
        narrative.append("Quiet minute: no notable events.")

    minute_summary["minute"] = minute_index
    minute_summary["score_total"] = new_total
    minute_summary["narrative"] = narrative
    minute_summary["coefficients"] = coefficients
    minute_summary["token"] = {
        "state": minute_summary["end_state"],
        "possession": minute_summary["possession_end"],
        "zone": minute_summary["zone_end"],
        "minute": minute_index + 1,
        "total_score": new_total,
        "coefficients": coefficients,
    }

    result = {
        "spec_version": spec.get("version"),
        "tick_seconds": spec["time"]["tick_seconds"],
        "regulation_minutes": int(spec["time"].get("regulation_minutes", 90)),
        "seed": seed_value,
        "teams": {"home": home_name, "away": away_name},
        "minute_summary": minute_summary,
    }

    resp = JsonResponse(result)
    origin = request.headers.get("Origin")
    if origin in ("http://127.0.0.1:5173", "http://localhost:5173"):
        resp["Access-Control-Allow-Origin"] = origin
        resp["Vary"] = "Origin"
    return resp
