from pathlib import Path
import os
from celery.schedules import crontab
from dotenv import load_dotenv

# === Base paths & .env ===
BASE_DIR = Path(__file__).resolve().parent.parent

from .whitenoise_headers import add_headers as whitenoise_add_headers
# ╨Ч╨░╨│╤А╤Г╨╢╨░╨╡╨╝ ╨┐╨╡╤А╨╡╨╝╨╡╨╜╨╜╤Л╨╡ ╨╛╨║╤А╤Г╨╢╨╡╨╜╨╕╤П ╨╕╨╖ .env ╨▓ ╨║╨╛╤А╨╜╨╡ ╨┐╤А╨╛╨╡╨║╤В╨░ (╤А╤П╨┤╨╛╨╝ ╤Б manage.py)
load_dotenv(BASE_DIR / ".env")

# 1) ╨а╨╡╨╢╨╕╨╝: ╨┐╤А╨╛╨┤ / ╨┤╨╡╨▓
IS_PRODUCTION = os.getenv('IS_PRODUCTION')  # '1' ╨┤╨╗╤П ╨┐╤А╨╛╨┤╨░╨║╤И╨╡╨╜╨░, ╨╕╨╜╨░╤З╨╡ dev

# ╨У╨╗╨╛╨▒╨░╨╗╤М╨╜╨░╤П "╤А╨╡╨░╨╗╤М╨╜╨░╤П" ╨┤╨╗╨╕╤В╨╡╨╗╤М╨╜╨╛╤Б╤В╤М ╨╕╨│╤А╨╛╨▓╨╛╨╣ ╨╝╨╕╨╜╤Г╤В╤Л (╤Б╨╡╨║╤Г╨╜╨┤╤Л).
# ╨Я╨╛╨┤╨┤╨╡╤А╨╢╨╕╨▓╨░╨╡╨╝ ╨╛╨▒╨░ ╨╜╨░╨╖╨▓╨░╨╜╨╕╤П ╨║╨╗╤О╤З╨░, ╤З╤В╨╛╨▒╤Л ╨╜╨╡ ╨╗╨╛╨╝╨░╤В╤М ╤Б╤Г╤Й╨╡╤Б╤В╨▓╤Г╤О╤Й╨╕╨╣ .env:
# - MATCH_MINUTE_REAL_SECONDS (╨╜╨╛╨▓╤Л╨╣)
# - MATCH_TICK_SECONDS       (╤Б╤В╨░╤А╤Л╨╣, ╨║╨░╨║ ╨▓ ╨▓╨░╤И╨╡╨╝ .env)
MATCH_MINUTE_REAL_SECONDS = int(
    os.getenv('MATCH_MINUTE_REAL_SECONDS', os.getenv('MATCH_TICK_SECONDS', 20))
)
TRAINING_CRON_DAYSOFWEEK = os.getenv("TRAINING_CRON_DAYSOFWEEK", "1,3,5")
TRAINING_CRON_HOUR = int(os.getenv("TRAINING_CRON_HOUR", 11))
TRAINING_CRON_MINUTE = int(os.getenv("TRAINING_CRON_MINUTE", 0))
TRAINING_TIMEZONE = os.getenv("TRAINING_TZ", "CET")
TRAINING_CHECK_INTERVAL_SECONDS = int(os.getenv("TRAINING_CHECK_INTERVAL_SECONDS", 1800))  # default: every 30 min
_CRON_TO_PY_WEEKDAY = {
    0: 6,  # Sunday (crontab) -> 6 (Python weekday)
    1: 0,  # Monday
    2: 1,  # Tuesday
    3: 2,  # Wednesday
    4: 3,  # Thursday
    5: 4,  # Friday
    6: 5,  # Saturday
    7: 6,  # Sunday (crontab allows 0 or 7)
}
TRAINING_DAY_LIST = [
    _CRON_TO_PY_WEEKDAY[int(x)]
    for x in TRAINING_CRON_DAYSOFWEEK.split(",")
    if x.strip().isdigit()
]

# Player Personality & Narrative AI Engine
USE_PERSONALITY_ENGINE = os.getenv('USE_PERSONALITY_ENGINE', 'True').lower() == 'true'

# === OpenAI (╨┤╨╗╤П ╨│╨╡╨╜╨╡╤А╨░╤Ж╨╕╨╕ ╨░╨▓╨░╤В╨░╤А╨╛╨▓) ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENABLE_AVATAR_GENERATION = str(os.getenv("OPENAI_ENABLE_AVATAR_GENERATION", "true")).lower() in ("1", "true", "yes")

# ╨С╨░╨╖╨╛╨▓╤Л╨╡ Django-╨╜╨░╤Б╤В╤А╨╛╨╣╨║╨╕
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")
debug_default = "0" if IS_PRODUCTION == "1" else "1"
DEBUG = str(os.getenv("DEBUG", os.getenv("DJANGO_DEBUG", debug_default))).lower() in ("1", "true", "yes")
allowed_hosts_env = os.getenv("ALLOWED_HOSTS")
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]
else:
    ALLOWED_HOSTS = ['128.199.49.228', 'www.realfootballsim.com', 'realfootballsim.com'] if IS_PRODUCTION == '1' else ['127.0.0.1', 'localhost']
csrf_origins_env = os.getenv("CSRF_TRUSTED_ORIGINS")
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_env.split(",") if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'https://realfootballsim.com',
        'https://www.realfootballsim.com'
    ] if IS_PRODUCTION == '1' else [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]

# ╨Х╤Б╨╗╨╕ ╨▓╨║╨╗╤О╤З╤С╨╜ ╨┐╤А╨╛╨┤╨░╨║╤И╨╡╨╜-╤А╨╡╨╢╨╕╨╝
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'core',
    'players.apps.PlayersConfig',  # <-- ╨▓╨░╨╢╨╜╨╛: ╤З╤В╨╛╨▒╤Л ready() ╨┐╨╛╨┤╨║╨╗╤О╤З╨░╨╗ ╤Б╨╕╨│╨╜╨░╨╗╤Л
    'clubs',
    'matches',
    'tournaments.apps.TournamentsConfig',
    'django_celery_beat',
    'channels',
    'transfers',
    'narrative',  # Story Center Dashboard
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tournaments.timezone_middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'realfootballsim.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",
            BASE_DIR / "static" / "front",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tournaments.context_processors.timezone_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'realfootballsim.wsgi.application'

# Channels
ASGI_APPLICATION = 'realfootballsim.asgi.application'

# База данных (локально PostgreSQL)
DB_NAME = os.getenv("DB_NAME", "rfsimdb")
DB_USER = os.getenv("DB_USER", "nikos")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

if IS_PRODUCTION == '1' and not DB_PASSWORD:
    raise ValueError("DB_PASSWORD must be set when IS_PRODUCTION=1")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'ATOMIC_REQUESTS': False,
    }
}

# ╨Я╤А╨╛╨┤╨░╨║╤И╨╡╨╜: ╨┐╤А╨╕ ╨╜╨╡╨╛╨▒╤Е╨╛╨┤╨╕╨╝╨╛╤Б╤В╨╕ ╨┐╨╡╤А╨╡╨╛╨┐╤А╨╡╨┤╨╡╨╗╤П╨╡╨╝ (╨╛╤Б╤В╨░╨▓╨╗╨╡╨╜╨╛ ╨║╨░╨║ ╤Г ╨▓╨░╤Б)
# Allow tests to opt-in to SQLite (avoids Postgres test DB conflicts)
if os.getenv("USE_SQLITE_FOR_TESTS") == "1":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise headers for fonts
WHITENOISE_ADD_HEADERS_FUNCTION = whitenoise_add_headers

# Media files (uploads) тАФ ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╤О╤В╤Б╤П ╨┤╨╗╤П ╨░╨▓╨░╤В╨░╤А╨╛╨▓ ╨╕╨│╤А╨╛╨║╨╛╨▓
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_REDIRECT_URL = 'core:home'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'core:home'

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 240
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_ROUTES = {}

CELERY_BEAT_SCHEDULE = {
    'simulate-active-matches': {
        'task': 'tournaments.simulate_active_matches',
        # ╨С╤Г╨┤╨╡╤В ╨┐╨╡╤А╨╡╨╛╨┐╤А╨╡╨┤╨╡╨╗╨╡╨╜╨╛ ╨▓ ╨С╨Ф ╨┤╨╛ MATCH_MINUTE_REAL_SECONDS
        'schedule': MATCH_MINUTE_REAL_SECONDS,
    },
    'advance-match-minutes': {
        'task': 'tournaments.advance_match_minutes',
        # Check more frequently than the threshold to avoid missing the window
        'schedule': 5.0, 
    },
    'check-season-end': {
        'task': 'tournaments.check_season_end',
        'schedule': crontab(hour=0, minute=0),
    },
    'start-scheduled-matches': {
        'task': 'tournaments.start_scheduled_matches',
        'schedule': 60.0,
    },
    'check-training-schedule': {
        'task': 'players.check_training_schedule',
        # run frequently to catch up missed runs after restarts; guarded by TRAINING_DAY_LIST inside
        'schedule': TRAINING_CHECK_INTERVAL_SECONDS or crontab(
            hour=TRAINING_CRON_HOUR,
            minute=TRAINING_CRON_MINUTE,
            day_of_week=TRAINING_CRON_DAYSOFWEEK,
        ),
    },
    'advance-player-seasons': {
        'task': 'players.advance_player_seasons',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'standard': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'match_creation_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'match_creation.log'),
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },

    'loggers': {
        'clubs':   {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': True},
        'matches': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': True},
        'tournaments': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': True},
        'match_creation': {'handlers': ['match_creation_handler'], 'level': 'INFO', 'propagate': False},
    },
}

TOURNAMENT_TIMEZONES = [
    ('UTC', 'UTC'),
    ('Europe/London', 'London'),
    ('Europe/Moscow', 'Moscow'),
    ('America/New_York', 'New York'),
    ('Asia/Tokyo', 'Tokyo'),
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
