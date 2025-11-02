from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml  # type: ignore
except Exception as e:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    raise

ALLOWED_STATES = {
    "KICKOFF",
    "OPEN_PLAY_DEF",
    "OPEN_PLAY_MID",
    "OPEN_PLAY_FINAL",
    "SHOT",
    "OUT",
    "FOUL",
    "GK",
}

def _sum_ok(values: Iterable[float], tol: float = 1e-6) -> bool:
    s = float(sum(values))
    return abs(s - 1.0) <= max(tol, 0.001)  # допуск на округление

def _ensure(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)

def validate_spec(spec: dict[str, Any]) -> None:
    # Базовые поля
    _ensure(spec.get("version") is not None, "version missing")
    time = spec.get("time") or {}
    _ensure(time.get("tick_seconds") == 10, "tick_seconds must be 10 in v0")
    _ensure(int(time.get("regulation_minutes", 0)) > 0, "regulation_minutes must be > 0")

    # Индекс состояний
    states = spec.get("states") or []
    name_to_state = {}
    for s in states:
        name = s.get("name")
        _ensure(name in ALLOWED_STATES, f"unknown state name: {name}")
        _ensure(name not in name_to_state, f"duplicate state: {name}")
        name_to_state[name] = s

    # Проверка по каждому состоянию
    for name, s in name_to_state.items():
        if "transitions" in s:
            probs = []
            for t in s["transitions"]:
                to = t.get("to")
                p = float(t.get("p", -1))
                poss = t.get("possession")
                _ensure(to in ALLOWED_STATES, f"{name}: transition to unknown state '{to}'")
                _ensure(0.0 <= p <= 1.0, f"{name}: invalid p={p} for to={to}")
                _ensure(poss in {"same", "opponent"}, f"{name}: invalid possession='{poss}'")
                probs.append(p)
            _ensure(_sum_ok(probs), f"{name}: transition probabilities must sum to 1.0 (got {sum(probs):.4f})")

        if "outcomes" in s:
            probs = []
            for oc in s["outcomes"]:
                p = float(oc.get("p", -1))
                nxt = oc.get("next") or {}
                to = nxt.get("to")
                poss = nxt.get("possession")
                _ensure(0.0 <= p <= 1.0, f"{name}: invalid outcome p={p}")
                _ensure(to in ALLOWED_STATES, f"{name}: outcome next->to unknown '{to}'")
                _ensure(poss in {"same", "opponent"}, f"{name}: outcome next->possession invalid '{poss}'")
                probs.append(p)
            _ensure(_sum_ok(probs), f"{name}: outcomes must sum to 1.0 (got {sum(probs):.4f})")

        if name == "OUT":
            bz = s.get("by_zone") or {}
            for zone, cfg in bz.items():
                dist = cfg.get("distribution") or []
                probs = []
                for t in dist:
                    to = t.get("to")
                    p = float(t.get("p", -1))
                    poss = t.get("possession")
                    _ensure(to in ALLOWED_STATES, f"OUT[{zone}]: to unknown '{to}'")
                    _ensure(0.0 <= p <= 1.0, f"OUT[{zone}]: invalid p={p}")
                    _ensure(poss in {"same", "opponent"}, f"OUT[{zone}]: invalid possession='{poss}'")
                    probs.append(p)
                _ensure(_sum_ok(probs), f"OUT[{zone}]: distribution must sum to 1.0 (got {sum(probs):.4f})")

        if name == "FOUL":
            bz = s.get("by_zone") or {}
            for zone, nxt in bz.items():
                to = (nxt or {}).get("to")
                poss = (nxt or {}).get("possession")
                _ensure(to in {"OPEN_PLAY_DEF", "OPEN_PLAY_MID", "OPEN_PLAY_FINAL"}, f"FOUL[{zone}]: invalid to='{to}'")
                _ensure(poss in {"same", "opponent"}, f"FOUL[{zone}]: invalid possession='{poss}'")

        if name == "GK":
            probs = [float(t.get("p", -1)) for t in s.get("transitions", [])]
            _ensure(_sum_ok(probs), f"GK: transitions must sum to 1.0 (got {sum(probs):.4f})")

    # Ссылки из всех переходов должны указывать на существующие состояния
    # (ALLOWED_STATES уже ограничивает множество допустимых имён)

def main() -> int:
    path = Path(__file__).with_name("markov_spec_v0.yaml")
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: spec file not found: {path}", file=sys.stderr)
        return 2
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        validate_spec(data)
    except AssertionError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1
    print("VALID: Markov spec v0 looks good.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
