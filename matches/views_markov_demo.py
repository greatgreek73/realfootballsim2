from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import random
import yaml
from django.http import JsonResponse

def _load_spec() -> Dict[str, Any]:
    """Читает YAML-спеку движка (v0)."""
    spec_path = Path(__file__).resolve().parent / "engines" / "markov_spec_v0.yaml"
    return yaml.safe_load(spec_path.read_text(encoding="utf-8"))

def _choose_weighted(rng: random.Random, items: list[dict]) -> dict:
    """Выбор по вероятностям p."""
    r = rng.random()
    acc = 0.0
    for item in items:
        acc += float(item.get("p", 0.0))
        if r <= acc:
            return item
    return items[-1]  # на случай округлений

def markov_demo(request):
    """
    Мини-демо: один вероятностный шаг из KICKOFF по YAML-спеке.
    Результат — JSON, чтобы можно было увидеть «живой» отклик движка.
    """
    spec = _load_spec()
    states = {s["name"]: s for s in spec.get("states", [])}
    seed_value = int(request.GET.get("seed", "73"))
    rng = random.Random(seed_value)

    kickoff = states["KICKOFF"]
    chosen = _choose_weighted(rng, kickoff["transitions"])

    result = {
        "spec_version": spec.get("version"),
        "tick_seconds": spec["time"]["tick_seconds"],
        "states_count": len(states),
        "seed": seed_value,
        "sample": {
            "from": "KICKOFF",
            "to": chosen.get("to"),
            "possession": chosen.get("possession"),
            "p": chosen.get("p"),
            # Отдадим любые дополнительные метки перехода (subtype/zone/kind):
            "meta": {k: v for k, v in chosen.items() if k not in ("to", "possession", "p")},
        },
    }
    resp = JsonResponse(result)
    origin = request.headers.get("Origin")
    if origin in ("http://127.0.0.1:5173", "http://localhost:5173"):
        resp["Access-Control-Allow-Origin"] = origin
        resp["Vary"] = "Origin"
    return resp

