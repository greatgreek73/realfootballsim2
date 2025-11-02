"""Compatibility shim: routes legacy match_simulation imports to Markov v1 stubs."""
from typing import Any
from matches.engines.markov_v1 import engine_stub

# Legacy function names expected across the codebase
simulate_one_action = engine_stub
simulate_match = engine_stub

def send_update(*args: Any, **kwargs: Any) -> None:
    """No-op during engine migration. Old code may call this to push UI updates."""
    return None

class MatchSimulation:
    """Minimal placeholder to keep management commands/tests importable."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
    def run(self) -> None:
        raise NotImplementedError("Markov engine WIP: MatchSimulation not implemented yet")

def __getattr__(name: str):
    """
    Fallback for any other legacy symbols imported from matches.match_simulation.
    This makes `from matches.match_simulation import some_old_func` succeed,
    but raises when called.
    """
    def _stub(*args: Any, **kwargs: Any):
        raise NotImplementedError(f"Markov engine WIP: '{name}' is not implemented yet")
    return _stub
