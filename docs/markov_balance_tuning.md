# Markov Balance Tuning (Step 8)

Purpose: how to validate/tune the new stat-driven coefficients without breaking determinism.

## Defaults
- Caps: most coeffs 0.7–1.3; fouls up to 1.4. These keep swings modest.
- Dampening: 0.4–0.5 to soften stat gaps.
- Missing stats fallback to neutral (~70), so incomplete data stays stable.

## Quick test matrix (manual/sim)
Run simulations (seeded) for pairs of teams:
1) Strong vs weak overall (att/def/GK all +20).
2) Strong GK vs strong finisher (swap sides).
3) High passing/vision vs high pressing/aggression.
4) Aerial monster vs ground-focused defense (to see headers vs normal shots).

Expected trends (not guarantees):
- Strong passer/vision keeps more possession and reaches more shots.
- Strong GK reduces goals, not to zero; strong finisher still scores some.
- High press raises turnovers/fouls slightly; good control reduces losses.
- Aerial edge shows slightly higher shot->goal on headers, but capped.

## Metrics to watch
- xG-ish: count shots and goals per 90 (per seed batch).
- Possession % and swings per minute.
- Fouls/cards frequency (if/when cards are added).
- Goal distribution: ensure not 0–0 every time and not blowouts every seed.

## Tuning levers (in `COEFF_CONFIG` in `markov_runtime.py`)
- `cap_low/cap_high`: tighten to reduce stat impact, loosen to increase.
- `dampen`: lower = stronger effect of stat gaps, higher = softer.
- Stat lists: adjust which fields are averaged for each context (e.g., add/remove strength for headers).

## Process
1) Pick fixed seeds and two roster setups (strong/weak) to keep comparisons deterministic.
2) Run batches (e.g., 100 minutes) and collect metrics above.
3) Adjust `COEFF_CONFIG` caps/dampen minimally, rerun, compare.
4) Stop when trends are visible (stronger team has edge) but scores/fouls remain plausible.

## Rollback safety
- Keep changes to `COEFF_CONFIG`; avoid altering spec until confident.
- Determinism is preserved (seed+token), so before/after runs are comparable.
