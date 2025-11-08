# RealFootballSim

This is a Django based football simulator featuring live match updates, player management, tournaments and a transfer market. Redis and Celery are used for asynchronous tasks and match simulation.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Database**
   The project expects PostgreSQL running locally with database name `rfsimdb`. Update `DATABASES` in `realfootballsim/settings.py` if needed.

3. **Environment variables**
   - `IS_PRODUCTION` - set to `1` to enable production settings.
   - `MATCH_MINUTE_REAL_SECONDS` - real seconds that represent one simulated minute (default: `60`).

4. **Running the project**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. **Celery workers**
   Celery requires Redis. Start a Redis server then run:
   ```bash
   celery -A realfootballsim worker -l info
   celery -A realfootballsim beat -l info
   ```

These workers drive match simulation and periodic season checks.

- **Dev fallback:** when Celery is not running you can still auto-simulate quick friendly matches by setting  `VITE_AUTO_SIMULATE_FRIENDLY=true` in a frontend `.env` file (for example `.env.development`). Leave it `false` in production so background workers drive the simulation. 

## Player Skills

Passing and shooting outcomes now take into account relevant attributes of the players involved. A well trained squad will perform better in live simulations.

## Tests

Run tests with:
```bash
pytest
```

Tests cover championships, season transitions and basic Celery task behaviour.

To re-run tests automatically while you edit Python files, start the watcher script (PowerShell):
```powershell
pwsh .\scripts\watch_tests.ps1
```
You can pass extra pytest arguments, for example to focus on a single test:
```powershell
pwsh .\scripts\watch_tests.ps1 --PytestArgs tests\test_utils.py::test_extract_player_id_handles_supported_inputs
```

## Frontend Layout Blueprint

All new application pages follow a single structural contract so that we can move fast without inventing a layout each time.

### PageShell contract

`frontend/src/components/ui/PageShell.tsx` defines the frame:

```
<PageShell
  hero={/* gradient banner */}
  top={/* optional intro card / tabs */}
  main={/* primary 2/3 content */}
  aside={/* optional 1/3 column */}
/>
```

- **Hero** — always rendered. Use `HeroBar` (`frontend/src/components/ui/HeroBar.tsx`) with a unique `tone`, `subtitle`, KPI list and optional `accent` chips/badges. The hero sets the “face” of the page, so avoid duplicating tones/KPIs across screens unless the experience is intentionally shared (e.g. Transfers vs Matches).
- **Top** — optional full-width card(s) for breadcrumbs, quick filters or short explanations.
- **Main** — the primary content block (tables, dashboards, forms). On desktop it spans 2/3 of the width; on mobile it stacks above everything else.
- **Aside** — optional supporting information (status summaries, tips, history lists). Leave it `undefined` if unused so the grid collapses to a single column.

### Authoring guidelines

1. **Always wrap new route components in `PageShell`.** Drop any ad‑hoc grid markup (MUI Grid, Tailwind columns, etc.) inside `main`/`aside` only.
2. **HeroBar usage**:
   - Pick a `tone` (`blue`, `green`, `purple`, `orange`, `teal`, `pink`) that is not already used on the same navigation level.
   - Populate 3‑4 KPI cards. Each entry supports an icon, primary value and optional `hint`.
   - Use the `actions` slot for navigation buttons (e.g. “Back to players”, “Create listing”).
   - Use the `accent` slot for chips summarising filters, counts or warnings.
3. **Top block** is a great place for breadcrumbs, short copy, filter descriptions or tabs. Keep it to lightweight content so it doesn’t compete with the hero.
4. **Tests/Reviews** — when opening a PR that adds or modifies a page, include a screenshot plus a short note describing the hero tone/KPIs you selected.

Following this blueprint keeps the dashboard predictable and lets us drop new features (Matches, Transfers, Squad flows) without layout churn.
