# Markov Runtime Backward Compatibility / Rollout (Step 10)

Scope: richer per-tick data (`dyn_context`, `actor_names`, labels/subtypes) and extended roster stats. No DB migrations are required; `markov_token` is JSONField and accepts extra keys.

Key points
- **Tokens**: Old tokens without `dyn_context` keep working; new tokens add it. Unknown keys are ignored on load; rollback is safe.
- **Roster stats**: Extra stats in `rosters_map` are optional; missing values default to neutral inside the engine. Passing `rosters=None` disables stat influence (hard fallback).
- **Logging**: `MARKOV_DEBUG_LOG=1` is opt-in; default behavior unchanged.
- **Events**: Labels/subtypes (`PASS`, `RETAIN`, `TURNOVER`, `SHOT:*`) are additive; consumers can ignore unknown fields.
- **Determinism**: Seed + token still fully determine outcomes; added fields do not break replay.

Rollout/rollback checklist
- Deploy without DB migration.
- If issues appear, unset `MARKOV_DEBUG_LOG` and/or call engine with `rosters=None` to revert to pre-stat behavior at runtime.
- Existing `markov_token` rows remain valid; no cleanup needed.
- If consumers choke on new fields, strip/ignore `label`, `subtype`, `dyn_context`, `actor_names` on client side until updated.
