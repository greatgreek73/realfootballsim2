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
   - `IS_PRODUCTION` – set to `1` to enable production settings.
   - `MATCH_MINUTE_REAL_SECONDS` – real seconds that represent one simulated minute (default: `60`).

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

## Player Skills

Passing and shooting outcomes now take into account relevant attributes of the players involved. A well trained squad will perform better in live simulations.

## Tests

Run tests with:
```bash
pytest
```

Tests cover championships, season transitions and basic Celery task behaviour.
