# Detailed Skill → Event Mapping (Plan Step 1)

Goal: Specify which player attributes should influence which outcomes so we can wire them into tick decisions.

## Open play: passing, progression, and press
- **Successful pass/progression (MID/FINAL)**: Attacker uses `passing`, `vision`, `dribbling`, `work_rate`, `composure`; Defender uses `marking`, `positioning`, `tackling`, `strength`, `work_rate`.
- **Press-induced turnover**: Holder uses `ball_control`, `balance`, `composure`; Presser uses `aggression`, `tackling`, `work_rate`, `positioning`.
- **Risky/long switch** (optional): Attacker `long_range`/`crossing`; Defender `interceptions`/`positioning` (if available).

## Final third: chance creation
- **Dribble/carry success**: `dribbling`, `balance`, `pace`, `work_rate` vs `tackling`, `positioning`, `strength`, `aggression`.
- **Pass into box / through ball**: `passing`, `vision`, `flair`, `work_rate` vs `marking`, `positioning`, `tackling`.

## Shots
- **Footed shot (close/medium)**: `finishing`, `accuracy`, `composure`; GK: `reflexes`, `handling`, `positioning`.
- **Long shot**: `long_range`, `accuracy`, `finishing`; GK: `positioning`, `handling`, `reflexes`.
- **Header / aerial**: `heading`, `strength`, `jumping`/`aerial`; GK/DEF: `aerial`, `positioning`, `strength`.
- **Shot block vs goal**: Attacker coeffs vs GK coeffs decide goal/miss/block weights.

## Goalkeeper restarts and outs
- **Goal kick / distribution accuracy**: GK `kicking`/`distribution`, `command`, `vision` vs presser’s `press` (work_rate/aggression/positioning).
- **Throw/short distribution safety**: `handling`, `command`, `vision` vs presser’s `press`.
- **Out balls (touchline/goal-line)**: Attacker `control`/`passing`; Defender `pressure` stats can force bad touch (press coeff).

## Fouls and discipline
- **Foul likelihood**: `aggression`, low `tackling`, low `balance`/`composure`.
- **Card likelihood**: `aggression` + low `discipline`/`composure`.
- **Possession after foul**: Attacker’s `control`/`balance`/`composure` vs defender’s `aggression`/`tackling` to decide who restarts.

## Pressing and turnovers
- **Press success**: `aggression`, `tackling`, `work_rate`, `positioning`.
- **Retention under press**: `ball_control`, `balance`, `vision`, `composure`.

## Optional/if available fields
- `discipline`, `composure`, `interceptions`, `jumping`, `agility`, `weak_foot`, `dominant_foot`. If absent, fallback to neutral value.

## Notes on integration
- Keep caps (e.g., 0.7–1.3) and dampening to avoid runaway effects.
- Missing stats must default to neutral; engine must remain deterministic with seed+token.
- Extend rosters to include the above fields where present; otherwise, safe defaults.
