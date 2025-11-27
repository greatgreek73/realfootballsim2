"""Reusable runtime helpers for Markov-minute simulation.

This module exposes a single public entry point, ``simulate_markov_minute``,
which can be safely imported both by Django views (for demo endpoints) and
background workers (Celery tasks, management commands, etc.).  The helper
returns a structured minute summary describing everything that happened during
the simulated minute together with the opaque token that allows the caller to
resume the process deterministically.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

import yaml

TICKS_PER_MINUTE = 6
SPEC_PATH = Path(__file__).resolve().parent / "markov_spec_v0.yaml"


class MarkovMinuteEvent(TypedDict, total=False):
    tick: int
    event: str
    type: str
    frm: str
    to: str
    possession: Optional[str]
    prev_possession: Optional[str]
    zone: Optional[str]
    label: Optional[str]
    subtype: Optional[str]
    turnover: bool
    narrative: Optional[str]


class MarkovToken(TypedDict, total=False):
    state: str
    possession: str
    zone: str
    minute: int
    total_score: Dict[str, int]
    coefficients: Dict[str, Dict[str, float]]


class MarkovMinuteSummary(TypedDict, total=False):
    """Structured minute contract consumed by ``Match`` state syncing code."""

    minute: int
    end_state: str
    possession_end: str
    zone_end: str
    score: Dict[str, int]
    score_total: Dict[str, int]
    counts: Dict[str, int]
    entries_final: Dict[str, int]
    possession_seconds: Dict[str, int]
    swings: int
    events: List[MarkovMinuteEvent]
    narrative: List[str]
    pure_narrative: List[str]
    token: MarkovToken
    coefficients: Dict[str, Dict[str, float]]


class MarkovMinuteResult(TypedDict):
    spec_version: Optional[str]
    tick_seconds: int
    regulation_minutes: int
    seed: int
    teams: Dict[str, str]
    minute_summary: MarkovMinuteSummary


@lru_cache(maxsize=1)
def _load_spec() -> Dict[str, Any]:
    return yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))


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

    if frm.startswith("OPEN_PLAY_") and to.startswith("OPEN_PLAY_"):
        if turnover:
            if to == "OPEN_PLAY_DEF":
                return f"Turnover! {who} win the ball and drop into defensive third"
            return f"Turnover sparks {who}'s move through {z}"
        if frm == to:
            return f"{who} probe patiently in the {z}"
        if to == "OPEN_PLAY_FINAL":
            return f"{who} advance into the final third"
        if to == "OPEN_PLAY_MID" and frm == "OPEN_PLAY_FINAL":
            return f"{who} recycle possession back to midfield"

    if frm == "SHOT":
        if label == "SHOT:goal":
            return f"Goal! {who} convert their chance"
        if label == "SHOT:miss":
            return f"{who} miss the target from the {z}"
        if label == "SHOT:block":
            return f"A defender blocks {who}'s effort"

    if frm == "FOUL":
        return f"Foul in the {z}. {who} retain control." if not turnover else f"Foul conceded. {who} take over."

    if frm == "OUT":
        if subtype == "throw_in":
            return f"Throw-in near the {z} for {who}"
        if subtype == "goal_kick":
            return f"Goal kick awarded to {who}"
        return f"Ball goes out. Restart favors {who}"

    if frm == "GK":
        return f"Goalkeeper restart for {who}"

    return None


def _summarize_tick(events: List[dict]) -> int:
    swings = 0
    prev = None
    for event in events:
        pos = event.get("possession")
        if prev and pos and pos != prev:
            swings += 1
        if pos:
            prev = pos
    return swings


def _push_event(
    events: List[dict],
    *,
    tick: int,
    frm: str,
    to: str,
    new_pos: Optional[str],
    new_zone: Optional[str],
    prev_pos: Optional[str],
    label: Optional[str] = None,
    subtype: Optional[str] = None,
    p: Optional[float] = None,
) -> None:
    ev = {
        "tick": tick,
        "from": frm,
        "to": to,
        "possession": new_pos,
        "prev_possession": prev_pos,
        "zone": new_zone,
        "turnover": (prev_pos is not None and new_pos is not None and new_pos != prev_pos),
    }
    if label is not None:
        ev["label"] = label
    if subtype is not None:
        ev["subtype"] = subtype
    if p is not None:
        ev["p"] = p
    events.append(ev)


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
                events,
                tick=tick,
                frm="SHOT",
                to=new_state,
                new_pos=new_pos,
                new_zone=new_zone,
                prev_pos=possession,
                label=f"SHOT:{result}",
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
                events,
                tick=tick,
                frm="OUT",
                to=new_state,
                new_pos=new_pos,
                new_zone=new_zone,
                prev_pos=possession,
                subtype=choice.get("subtype"),
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
                events,
                tick=tick,
                frm="FOUL",
                to=new_state,
                new_pos=new_pos,
                new_zone=new_zone,
                prev_pos=possession,
            )
            if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
                entries_final[new_pos] += 1
            state, possession, zone = new_state, new_pos, new_zone
            continue

        if state == "GK":
            tr = states["GK"]["transitions"][0]
            counts["gk"] += 1
            new_state = tr.get("to")
            new_pos = _apply_possession(possession, tr.get("possession", "same"))
            new_zone = _zone_from_state(new_state)
            _push_event(
                events,
                tick=tick,
                frm="GK",
                to=new_state,
                new_pos=new_pos,
                new_zone=new_zone,
                prev_pos=possession,
            )
            if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
                entries_final[new_pos] += 1
            state, possession, zone = new_state, new_pos, new_zone
            continue

        transitions = states[state]["transitions"]
        transitions = _adjust_advancing_transitions(
            transitions,
            state=state,
            possession=possession,
            attack_coeffs=attack_coeffs,
            defense_coeffs=defense_coeffs,
        )
        choice = _choose_weighted(rng, transitions)
        new_state = choice.get("to")
        new_pos = _apply_possession(possession, choice.get("possession", "same"))
        new_zone = choice.get("zone", _zone_from_state(new_state))
        _push_event(
            events,
            tick=tick,
            frm=state,
            to=new_state,
            new_pos=new_pos,
            new_zone=new_zone,
            prev_pos=possession,
            p=choice.get("p"),
        )
        if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
            entries_final[new_pos] += 1
        state, possession, zone = new_state, new_pos, new_zone

    swings = _summarize_tick(events)
    possession_seconds = {
        team: int(ticks * (spec["time"]["tick_seconds"] / 1.0)) for team, ticks in possession_ticks.items()
    }
    return {
        "end_state": state,
        "possession_end": possession,
        "zone_end": zone,
        "score": score,
        "counts": counts,
        "entries_final": entries_final,
        "possession_seconds": possession_seconds,
        "events": events,
        "swings": swings,
    }


def _parse_coeff(value: Any, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        parsed = float(value)
    else:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return default
    if not (0.01 <= parsed <= 10.0):
        return default
    return parsed


@dataclass
class MarkovState:
    state: str = "KICKOFF"
    possession: str = "home"
    zone: str = "MID"
    minute: int = 1
    total_score: Dict[str, int] = None  # type: ignore[assignment]
    coefficients: Dict[str, Dict[str, float]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.total_score is None:
            self.total_score = {"home": 0, "away": 0}
        if self.coefficients is None:
            self.coefficients = {
                "attack": {"home": 1.0, "away": 1.0},
                "defense": {"home": 1.0, "away": 1.0},
            }

    @classmethod
    def from_token(cls, token: Optional[dict]) -> "MarkovState":
        state = cls()
        if not isinstance(token, dict):
            return state
        state.state = token.get("state", state.state)
        state.possession = token.get("possession", state.possession)
        state.zone = token.get("zone", state.zone)
        state.minute = int(token.get("minute", state.minute))
        total_score = token.get("total_score")
        if isinstance(total_score, dict):
            state.total_score["home"] = int(total_score.get("home", 0))
            state.total_score["away"] = int(total_score.get("away", 0))
        coeffs = token.get("coefficients")
        if isinstance(coeffs, dict):
            for key in ("attack", "defense"):
                if key not in coeffs or not isinstance(coeffs[key], dict):
                    continue
                for side in ("home", "away"):
                    raw_value = coeffs[key].get(side)
                    state.coefficients.setdefault(key, {})
                    state.coefficients[key][side] = _parse_coeff(
                        raw_value,
                        state.coefficients[key].get(side, 1.0),
                    )
        return state


def simulate_markov_minute(
    *,
    seed: int,
    token: Optional[dict] = None,
    home_name: str = "Home",
    away_name: str = "Away",
    attack_override: Optional[Dict[str, Any]] = None,
    defense_override: Optional[Dict[str, Any]] = None,
) -> MarkovMinuteResult:
    """Simulate a single Markov minute and return a structured summary."""

    spec = _load_spec()
    state = MarkovState.from_token(token)

    def _apply_overrides(target: Dict[str, float], override: Optional[Dict[str, Any]]) -> Dict[str, float]:
        if not override:
            return target
        updated = dict(target)
        for side in ("home", "away"):
            if side in override:
                updated[side] = _parse_coeff(override[side], updated.get(side, 1.0))
        return updated

    state.coefficients["attack"] = _apply_overrides(state.coefficients["attack"], attack_override)
    state.coefficients["defense"] = _apply_overrides(state.coefficients["defense"], defense_override)

    rng = _rng_from(seed, state.minute, state.state, state.possession, state.zone)
    minute_summary = _simulate_minute(
        spec,
        rng,
        start_state=state.state,
        start_possession=state.possession,
        start_zone=state.zone,
        attack_coeffs=state.coefficients["attack"],
        defense_coeffs=state.coefficients["defense"],
    )

    new_total = {
        "home": state.total_score["home"] + minute_summary["score"]["home"],
        "away": state.total_score["away"] + minute_summary["score"]["away"],
    }

    narrative: List[str] = []
    pure_narrative: List[str] = []

    if state.minute == 1 and state.state == "KICKOFF":
        pure_narrative.append(f"Kick-off by {_side_name(state.possession, home_name, away_name)}")
    elif state.minute == 46 and state.state == "KICKOFF":
        pure_narrative.append(f"Second-half kick-off by {_side_name(state.possession, home_name, away_name)}")

    for event in minute_summary.get("events", []):
        text = _event_phrase(event, home_name, away_name)
        if text:
            event["narrative"] = text
            narrative.append(text)

    if not pure_narrative and not narrative:
        pure_narrative.append("Quiet minute: no notable events.")

    minute_summary["minute"] = state.minute
    minute_summary["score_total"] = new_total
    minute_summary["pure_narrative"] = pure_narrative
    minute_summary["narrative"] = pure_narrative + narrative
    minute_summary["coefficients"] = state.coefficients
    minute_summary["token"] = {
        "state": minute_summary["end_state"],
        "possession": minute_summary["possession_end"],
        "zone": minute_summary["zone_end"],
        "minute": state.minute + 1,
        "total_score": new_total,
        "coefficients": state.coefficients,
    }

    return {
        "spec_version": spec.get("version"),
        "tick_seconds": int(spec["time"].get("tick_seconds", 10)),
        "regulation_minutes": int(spec["time"].get("regulation_minutes", 90)),
        "seed": seed,
        "teams": {"home": home_name, "away": away_name},
        "minute_summary": minute_summary,
    }


def serialize_token(token: Optional[MarkovToken]) -> str:
    """Helper that makes it trivial to pass tokens over the wire."""
    return json.dumps(token or {})
