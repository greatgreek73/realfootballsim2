# Markov Runtime Backward Compatibility (Step 10)

Scope: recent changes added richer per-tick data (`dyn_context`, `actor_names`) and extended roster stats. No DB migrations are required; `markov_token` is a JSONField and accepts extra keys.

Key points
- **Tokens**: Old tokens without `dyn_context` continue to work; new tokens include it. `MarkovState.from_token` ignores unknown keys, so rollback is safe.
- **Roster stats**: Extra stats in `rosters_map` are optional; missing values default to neutral inside the engine. Older callers that passed `rosters=None` remain supported.
- **Logging**: Optional `MARKOV_DEBUG_LOG=1` is off by default; no behavior change unless set.
- **Failure mode**: If any new field is absent or malformed, code falls back to defaults and clamps coefficients, preserving deterministic behavior.

Rollout/rollback checklist
- Deploy without DB migration.
- If issues appear, unset `MARKOV_DEBUG_LOG` and/or pass `rosters=None` to revert to pre-stat influence behavior at runtime.
- Existing `markov_token` rows remain valid; no cleanup needed.
