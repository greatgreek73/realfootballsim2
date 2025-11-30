# Player Attribute → Match-Situation Mapping (Step 1)

Purpose: declare which player stats should influence which parts of the Markov tick so later steps can wire them into probabilities without guessing.

## Zones and lines
- **DEF**: defending team’s DEF vs pressing team’s FWD.
- **MID**: MID vs MID (fallback to DEF if empty).
- **FINAL**: attacking team’s FWD/AM vs defending team’s DEF.
- **SHOT**: attacker (FWD/AM/MID) vs goalkeeper.

## Open-play transitions (MID/FINAL)
- **Progress MID → FINAL**
  - Attacker: `passing`, `vision`, `dribbling`, `work_rate`.
  - Defender: `marking`, `positioning`, `tackling`, `strength`.
- **Progress FINAL → SHOT**
  - Attacker: `dribbling`, `finishing`, `flair` (if available), `work_rate`.
  - Defender: `marking`, `positioning`, `tackling`, `strength`.
- **Hold vs turnover (same-state stay or possession flip)**
  - Holder: `ball_control`, `balance` (if present), `vision`.
  - Presser: `tackling`, `aggression`, `work_rate`.

## Shot resolution
- **Attacker stats**: `finishing`, `long_range`, `accuracy`, `composure` (if present).
- **Goalkeeper stats**: `reflexes`, `handling`, `positioning`, `aerial`, `command`.
- **Contextual**: distance/subtype can map to `long_range` weight; headers could map to `aerial`.

## Foul likelihood and outcome
- **Foul risk (committing)**: `aggression`, `strength`, low `tackling`, low `balance`.
- **Drawing/evading fouls**: `dribbling`, `agility`/`balance`, `ball_control`.
- **Possession after foul**: defender’s `positioning` + attacker’s `control` decide who restarts if model allows.

## Out-of-play / restarts
- **Throw-in / generic restart**: minimal influence; can bias by `work_rate`/`vision`.
- **Goal kick**: goalkeeper `command`, `kicking` (if present) can bias toward safer vs longer restarts.

## Keep possession ticks (GK / recycling)
- Goalkeeper distribution: `kicking`, `command`, `vision`.
- Recycling in MID: `passing`, `vision`; disruption by presser's `marking`, `work_rate`.

## Debug / observability
- Minute summaries carry `actor_names` per tick and `dyn_context` (per-tick coefficient packs).
- Markov events now keep `label`/`subtype` in the payload (`PASS`, `RETAIN`, `TURNOVER`, `SHOT:goal/miss/block`, etc.) for richer logs and WS consumers.
- Set `MARKOV_DEBUG_LOG=1` to emit a short log line per simulated minute with seed, minute, end state, score, and dyn_context keys (not values).

## Data needed per player in roster payload
Recommended minimal fields to pass into `rosters`:
- Core: `overall`, `passing`, `vision`, `dribbling`, `finishing`, `long_range`, `accuracy`, `work_rate`, `ball_control`, `balance`, `aggression`, `tackling`, `marking`, `positioning`, `strength`.
- GK: `reflexes`, `handling`, `aerial`, `command`, `kicking`.
- Optional if available: `flair`, `composure`, `agility`.

Note: Until later steps hook these into code, missing fields should default to neutral values (e.g., 70 or coefficient 1.0) to remain backward compatible.
