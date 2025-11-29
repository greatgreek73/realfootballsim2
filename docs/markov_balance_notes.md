# Markov Balance & UX Notes (Step 11)

Targets
- Keep coefficients mild: caps currently 0.7–1.3 (shots 0.7–1.3, fouls cap 1.4). Avoid swingy results when ratings differ a lot.
- Preserve neutrality when stats are missing: defaults to ~70 and clamps ensure stability.

Suggested QA scenarios (manual/smoke)
- 90 vs 60 attacker in FINAL: expect higher progress/shot probability, but not guaranteed every tick.
- 60 vs 90 attacker in FINAL: expect more turnovers/blocks; match still produces shots.
- Strong GK vs weak shooter: goal chance falls but not to zero.
- High aggression tackler vs agile dribbler: foul flips possession a bit more often.

Tuning levers
- `COEFF_CONFIG` in `markov_runtime.py`: adjust `dampen` to soften/harden impact; adjust `cap_low`/`cap_high` to bound extremes; tweak stat lists per context.
- Roster stats: ensure upstream provides relevant stats; missing stats revert to neutral.
- Logging: use `MARKOV_DEBUG_LOG=1` and minute summaries (`dyn_context`, `actor_names`) to see per-tick coefficients.

UX notes
- Keep timeline readable: actor_names per tick are available for richer commentary.
- Determinism: seed+token still drive deterministic playback; added fields do not break replay.
