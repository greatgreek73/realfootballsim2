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

COEFF_CONFIG = {
    "progress_mid": {
        "att": ["passing", "vision", "dribbling", "work_rate"],
        "def": ["tackling", "marking", "positioning", "strength"],
        "dampen": 0.5,
        "cap_low": 0.7,
        "cap_high": 1.3,
    },
    "progress_final": {
        "att": ["dribbling", "finishing", "flair", "work_rate"],
        "def": ["marking", "tackling", "positioning", "strength"],
        "dampen": 0.5,
        "cap_low": 0.7,
        "cap_high": 1.3,
    },
    "shot": {
        "att": ["finishing", "long_range", "accuracy", "composure"],
        "def": ["reflexes", "handling", "positioning", "aerial", "command"],
        "dampen": 0.4,
        "cap_low": 0.7,
        "cap_high": 1.3,
    },
    "retain": {
        "att": ["ball_control", "balance", "vision", "work_rate"],
        "def": ["tackling", "aggression", "work_rate", "marking"],
        "dampen": 0.4,
        "cap_low": 0.7,
        "cap_high": 1.3,
    },
    "foul": {
        "commit": ["aggression", "strength", "tackling"],
        "draw": ["dribbling", "balance", "ball_control"],
        "dampen": 0.3,
        "cap_low": 0.7,
        "cap_high": 1.4,
    },
}


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
    dyn_context: Dict[str, float]


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
    dyn_context: Dict[str, float]
    actor_names: Dict[int, str]  # tick -> actor name


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
    dynamic_attack: float | None = None,
    dynamic_defense: float | None = None,
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
            
            # Use dynamic per-tick coeffs if provided, otherwise fall back to global coeffs
            attack = dynamic_attack if dynamic_attack is not None else attack_coeffs.get(team, 1.0)
            defense = dynamic_defense if dynamic_defense is not None else defense_coeffs.get(opponent, 1.0)
            
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


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _safe_stat(stats: Optional[Dict[str, Any]], key: str, default: float = 70.0) -> float:
    if not stats:
        return default
    raw = stats.get(key)
    try:
        val = float(raw)
        # reject nan/inf
        if val != val or val in (float("inf"), float("-inf")):  # pragma: no cover - safety
            return default
        return val
    except (TypeError, ValueError):
        return default


def _avg_stats(stats: Optional[Dict[str, Any]], keys: List[str], default: float = 70.0) -> float:
    vals = [_safe_stat(stats, k, default) for k in keys if k]
    return sum(vals) / len(vals) if vals else default


def _ratio_to_coeff(
    att_value: float,
    def_value: float,
    *,
    dampen: float = 0.5,
    cap_low: float = 0.7,
    cap_high: float = 1.3,
) -> tuple[float, float]:
    """
    Convert attacker vs defender values into (attack_coeff, defense_coeff),
    symmetric around 1.0, mildly dampened and clamped.
    """
    att_value = max(att_value, 1e-3)
    def_value = max(def_value, 1e-3)
    ratio = att_value / def_value
    delta = (ratio - 1.0) * dampen
    att_coeff = _clamp(1.0 + delta, cap_low, cap_high)
    def_coeff = _clamp(1.0 - delta, cap_low, cap_high)
    return att_coeff, def_coeff


def compute_coeff_pack(
    attacker: Optional[Dict[str, Any]],
    defender: Optional[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Build a set of per-context coefficients from rich player stats.
    This is NOT wired into transitions yet (used in later steps).
    Keys are symmetric multipliers around 1.0 with caps.
    """
    att_stats = attacker.get("stats") if attacker else {}
    def_stats = defender.get("stats") if defender else {}

    # Progressing through midfield
    cfg_mid = COEFF_CONFIG["progress_mid"]
    mid_att = _avg_stats(att_stats, cfg_mid["att"])
    mid_def = _avg_stats(def_stats, cfg_mid["def"])
    mid_attack, mid_defense = _ratio_to_coeff(
        mid_att,
        mid_def,
        dampen=cfg_mid["dampen"],
        cap_low=cfg_mid["cap_low"],
        cap_high=cfg_mid["cap_high"],
    )

    # Progressing in final third
    cfg_final = COEFF_CONFIG["progress_final"]
    final_att = _avg_stats(att_stats, cfg_final["att"])
    final_def = _avg_stats(def_stats, cfg_final["def"])
    final_attack, final_defense = _ratio_to_coeff(
        final_att,
        final_def,
        dampen=cfg_final["dampen"],
        cap_low=cfg_final["cap_low"],
        cap_high=cfg_final["cap_high"],
    )

    # Shot vs keeper
    cfg_shot = COEFF_CONFIG["shot"]
    shot_att = _avg_stats(att_stats, cfg_shot["att"])
    gk_def = _avg_stats(def_stats, cfg_shot["def"])
    shot_attack, gk_save = _ratio_to_coeff(
        shot_att,
        gk_def,
        dampen=cfg_shot["dampen"],
        cap_low=cfg_shot["cap_low"],
        cap_high=cfg_shot["cap_high"],
    )

    # Retention vs press (stay in same state)
    cfg_retain = COEFF_CONFIG["retain"]
    retain_att = _avg_stats(att_stats, cfg_retain["att"])
    press_def = _avg_stats(def_stats, cfg_retain["def"])
    retain, press = _ratio_to_coeff(
        retain_att,
        press_def,
        dampen=cfg_retain["dampen"],
        cap_low=cfg_retain["cap_low"],
        cap_high=cfg_retain["cap_high"],
    )

    # Foul tendencies
    cfg_foul = COEFF_CONFIG["foul"]
    foul_commit_raw = _avg_stats(att_stats, cfg_foul["commit"])
    foul_draw_raw = _avg_stats(def_stats, cfg_foul["draw"])
    foul_commit, _ = _ratio_to_coeff(
        foul_commit_raw,
        foul_draw_raw,
        dampen=cfg_foul["dampen"],
        cap_low=cfg_foul["cap_low"],
        cap_high=cfg_foul["cap_high"],
    )
    # Foul_draw here is inverse: higher means attacker more likely to draw a foul
    foul_draw, _ = _ratio_to_coeff(
        foul_draw_raw,
        foul_commit_raw,
        dampen=cfg_foul["dampen"],
        cap_low=cfg_foul["cap_low"],
        cap_high=cfg_foul["cap_high"],
    )

    return {
        "progress_mid_attack": mid_attack,
        "progress_mid_defense": mid_defense,
        "progress_final_attack": final_attack,
        "progress_final_defense": final_defense,
        "shot_attack": shot_attack,
        "gk_save": gk_save,
        "retain": retain,
        "press": press,
        "foul_commit": foul_commit,
        "foul_draw": foul_draw,
    }


def _adjust_shot_outcomes(
    outcomes: List[dict],
    *,
    shot_attack: float = 1.0,
    gk_save: float = 1.0,
) -> List[dict]:
    """
    Re-weights SHOT outcomes so stronger attackers raise goal chance while
    stronger keepers lower it. Keeps shape by normalizing.
    """
    if not outcomes:
        return outcomes
    adjusted = []
    total = 0.0
    for oc in outcomes:
        base_p = float(oc.get("p", 0.0))
        if base_p <= 0.0:
            continue
        label = str(oc.get("result") or oc.get("label") or "").lower()
        mult = 1.0
        if "goal" in label:
            mult = shot_attack / max(gk_save, 0.01)
        elif "block" in label:
            mult = gk_save / max(shot_attack, 0.01)
        elif "miss" in label:
            mult = 1.0  # neutral
        new_p = base_p * mult
        copy = dict(oc)
        copy["p"] = new_p
        adjusted.append(copy)
        total += new_p
    if total <= 0.0:
        return outcomes
    for oc in adjusted:
        oc["p"] = oc["p"] / total
    return adjusted


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
    
    # Use specific actor name if available, otherwise team name
    actor = e.get("actor_name")
    who = actor if actor else _side_name(pos, home_name, away_name)
    
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
    actor_name: Optional[str] = None,
    actor_id: Optional[str | int] = None,
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
    if actor_name:
        ev["actor_name"] = actor_name
    if actor_id:
        ev["actor_id"] = actor_id
    events.append(ev)


# Helper to select players based on zone
def _select_interaction_pair(
    rng: random.Random,
    rosters: Dict[str, Dict[str, List[Dict[str, Any]]]],
    attacker_side: str,
    zone: str,
    *,
    force_goalkeeper: bool = False,
) -> tuple[Optional[Dict], Optional[Dict]]:
    """Selects (attacker, defender) pair based on zone."""
    if not rosters or attacker_side not in rosters:
        return None, None

    defender_side = "away" if attacker_side == "home" else "home"
    
    # Map zone to likely player lines
    # DEF: Attacker is DEF, Defender is FWD (pressing)
    # MID: Attacker is MID, Defender is MID
    # FINAL: Attacker is FWD, Defender is DEF
    if force_goalkeeper:
        att_line, def_line = "FWD", "GK"
    elif zone == "DEF":
        att_line, def_line = "DEF", "FWD"
    elif zone == "FINAL":
        att_line, def_line = "FWD", "DEF"
    else:  # MID
        att_line, def_line = "MID", "MID"

    # Helper to pick random player from line
    def pick(side, line, *, allow_gk=False):
        pool = rosters.get(side, {}).get(line, [])
        if not pool and allow_gk:
            pool = rosters.get(side, {}).get("GK", [])
        # Fallback to MID if preferred line empty (e.g. no FWDs in formation)
        if not pool:
             pool = rosters.get(side, {}).get("MID", [])
        # Fallback to DEF
        if not pool:
             pool = rosters.get(side, {}).get("DEF", [])
        if not pool:
            return None
        return rng.choice(pool)

    attacker = pick(attacker_side, att_line)
    defender = pick(defender_side, def_line, allow_gk=force_goalkeeper)
    return attacker, defender


def _calculate_player_coeffs(attacker: Dict, defender: Dict) -> tuple[float, float]:
    """Calculates dynamic attack/defense coeffs relative to 1.0 base."""
    if not attacker or not defender:
        return 1.0, 1.0

    # Simple logic: compare overall ratings
    # If att > def, attack_coeff > 1.0, def_coeff < 1.0
    # We want a subtle effect. Max swing +/- 20%?
    
    att_rating = attacker.get("stats", {}).get("overall", 70)
    def_rating = defender.get("stats", {}).get("overall", 70)

    # Ensure non-zero
    att_rating = max(10, att_rating)
    def_rating = max(10, def_rating)

    # Ratio
    ratio = att_rating / def_rating
    
    # Dampen the ratio so it's not too extreme
    # e.g. 90 vs 70 -> 1.28 ratio. 
    # We might want to return (1.14, 0.86) roughly
    if ratio > 1:
        # Attacker stronger
        # attack=1.1, defense=0.9 for ratio=1.2
        boost = (ratio - 1.0) * 0.5 # dampen by half
        return 1.0 + boost, 1.0 / (1.0 + boost)
    else:
        # Defender stronger (ratio < 1)
        # ratio=0.8 -> def stronger
        # boost is negative
        boost = (1.0 - ratio) * 0.5
        return 1.0 - boost, 1.0 + boost


def _simulate_minute(
    spec: Dict[str, Any],
    rng: random.Random,
    *,
    start_state: str = "KICKOFF",
    start_possession: str = "home",
    start_zone: str | None = None,
    attack_coeffs: Dict[str, float] | None = None,
    defense_coeffs: Dict[str, float] | None = None,
    rosters: Dict[str, Dict[str, List[Dict[str, Any]]]] | None = None,
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
    dyn_context: Dict[int, Dict[str, float]] = {}
    actor_names: Dict[int, str] = {}

    for tick in range(1, TICKS_PER_MINUTE + 1):
        possession_ticks[possession] += 1
        
        # Select Actors for this tick
        # We check zone to decide who is likely involved
        tick_zone = zone # current zone
        if state == "SHOT": tick_zone = "FINAL" # shots happen in final
        
        protag, antag = None, None
        dyn_att, dyn_def = None, None
        dyn_pack = None

        if rosters:
            # In SHOT, force defender as GK to reflect finish vs keeper duel
            force_gk = state == "SHOT"
            protag, antag = _select_interaction_pair(
                rng, rosters, possession, tick_zone, force_goalkeeper=force_gk
            )
            if protag and antag:
                dyn_att, dyn_def = _calculate_player_coeffs(protag, antag)
                dyn_pack = compute_coeff_pack(protag, antag)
            elif protag:
                dyn_pack = compute_coeff_pack(protag, None)

        if dyn_pack:
            dyn_context[tick] = dyn_pack

        actor_name = protag.get("name") if protag else None
        actor_id = protag.get("id") if protag else None
        if actor_name:
            actor_names[tick] = actor_name

        if state == "SHOT":
            shot_outcomes = states["SHOT"]["outcomes"]
            if dyn_pack:
                shot_outcomes = _adjust_shot_outcomes(
                    shot_outcomes,
                    shot_attack=dyn_pack.get("shot_attack", 1.0),
                    gk_save=dyn_pack.get("gk_save", 1.0),
                )
            oc = _choose_weighted(rng, shot_outcomes)
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
                actor_name=actor_name,
                actor_id=actor_id,
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
                actor_name=actor_name,
                actor_id=actor_id,
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
            base_dir = nxt.get("possession", "same")
            new_pos = _apply_possession(possession, base_dir)
            if dyn_pack:
                # Bias possession after foul: attacker with high foul_draw keeps ball more often,
                # aggressive tackler flips it more often. Keep bounded to avoid large swings.
                keep_bias = dyn_pack.get("foul_draw", 1.0)
                commit_bias = dyn_pack.get("foul_commit", 1.0)
                # baseline 0.5, skewed by ratio; clamp to [0.25, 0.75] to stay mild
                keep_prob = _clamp(0.5 * keep_bias / max(commit_bias, 0.01), 0.25, 0.75)
                if rng.random() > keep_prob:
                    if new_pos == "home":
                        new_pos = "away"
                    elif new_pos == "away":
                        new_pos = "home"
            new_zone = _zone_from_state(new_state)
            _push_event(
                events,
                tick=tick,
                frm="FOUL",
                to=new_state,
                new_pos=new_pos,
                new_zone=new_zone,
                prev_pos=possession,
                actor_name=actor_name,
                actor_id=actor_id,
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
                actor_name=actor_name,
                actor_id=actor_id,
            )
            if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
                entries_final[new_pos] += 1
            state, possession, zone = new_state, new_pos, new_zone
            continue

        transitions = states[state]["transitions"]
        # Prefer contextual coeffs when available; fallback to coarse overall ratio
        dyn_attack = dyn_att
        dyn_defense = dyn_def
        if dyn_pack and state == "OPEN_PLAY_MID":
            dyn_attack = dyn_pack.get("progress_mid_attack", dyn_attack)
            dyn_defense = dyn_pack.get("progress_mid_defense", dyn_defense)
        elif dyn_pack and state == "OPEN_PLAY_FINAL":
            dyn_attack = dyn_pack.get("progress_final_attack", dyn_attack)
            dyn_defense = dyn_pack.get("progress_final_defense", dyn_defense)

        transitions = _adjust_advancing_transitions(
            transitions,
            state=state,
            possession=possession,
            attack_coeffs=attack_coeffs,
            defense_coeffs=defense_coeffs,
            dynamic_attack=dyn_attack,
            dynamic_defense=dyn_defense,
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
            actor_name=actor_name,
            actor_id=actor_id,
        )
        if new_state == "OPEN_PLAY_FINAL" and state != "OPEN_PLAY_FINAL":
            entries_final[new_pos] += 1
        state, possession, zone = new_state, new_pos, new_zone

    swings = _summarize_tick(events)
    possession_seconds = {
        team: int(ticks * (spec["time"]["tick_seconds"] / 1.0)) for team, ticks in possession_ticks.items()
    }
    dyn_context_str = {str(k): v for k, v in dyn_context.items()}
    actor_names_str = {str(k): v for k, v in actor_names.items()}

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
        "rosters_snapshot": rosters is not None,
        "dyn_context": dyn_context_str,
        "actor_names": actor_names_str,
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
    rosters: Optional[Dict[str, Dict[str, List[Dict[str, Any]]]]] = None,
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
        rosters=rosters,
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
    minute_summary["dyn_context"] = minute_summary.get("dyn_context", {})
    minute_summary["token"] = {
        "state": minute_summary["end_state"],
        "possession": minute_summary["possession_end"],
        "zone": minute_summary["zone_end"],
        "minute": state.minute + 1,
        "total_score": new_total,
        "coefficients": state.coefficients,
        "dyn_context": minute_summary["dyn_context"],
    }

    # Optional debug logging for observability; controlled via env var MARKOV_DEBUG_LOG
    import os
    if os.environ.get("MARKOV_DEBUG_LOG"):
        import logging
        dbg = logging.getLogger(__name__)
        dbg.info(
            "[markov_minute] seed=%s minute=%s end_state=%s score=%s dyn=%s",
            seed,
            state.minute,
            minute_summary["end_state"],
            new_total,
            minute_summary["dyn_context"],
        )

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
