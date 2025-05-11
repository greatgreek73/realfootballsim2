from pathlib import Path
import os
from celery.schedules import crontab

# 1) Check if we're in production (IS_PRODUCTION=1) or dev (IS_PRODUCTION != '1')
IS_PRODUCTION = os.environ.get('IS_PRODUCTION')  # If not set, will be None

BASE_DIR = Path(__file__).resolve().parent.parent

# Default dev settings
SECRET_KEY = 'django-insecure-0p3aqax2r2xolyvtfda6q_aa@q1l6n!w4$8sjo1ed&*)h*2l37'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# If production environment variable is set, override specific settings
if IS_PRODUCTION == '1':
    DEBUG = False
    ALLOWED_HOSTS = ['128.199.49.228', 'www.realfootballsim.com', 'realfootballsim.com']

    CSRF_TRUSTED_ORIGINS = [
    'https://realfootballsim.com',
    'https://www.realfootballsim.com'
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'core',
    'players',
    'clubs',
    'matches',
    'tournaments.apps.TournamentsConfig',
    'django_celery_beat',
    'channels',  # Добавляем channels
    'transfers',  # Явное указание конфига приложения
]

MIDDLEWARE = [
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Настройка Channels
ASGI_APPLICATION = 'realfootballsim.asgi.application'

# Настройка базы данных PostgreSQL для локальной разработки
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rfsimdb',
        'USER': 'nikos',
        'PASSWORD': '5x9t8zy5',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': False,
    }
}


# Если установлен IS_PRODUCTION, используем PostgreSQL
if IS_PRODUCTION == '1':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'rfsimdb',
            'USER': 'nikos',
            'PASSWORD': '5x9t8zy5',
            'HOST': 'localhost',
            'PORT': '5432',
            'ATOMIC_REQUESTS': False,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_REDIRECT_URL = 'clubs:club_detail'
LOGIN_URL = 'accounts:login'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Настройки Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 240

CELERY_WORKER_MAX_TASKS_PER_CHILD = 50
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Обновляем расписание задач Celery Beat
CELERY_BEAT_SCHEDULE = {
    'simulate-every-5-seconds': {
        'task': 'tournaments.simulate_active_matches',
        'schedule': 5.0,
    },
    'check-season-end': {
        'task': 'tournaments.check_season_end',
        'schedule': crontab(hour=0, minute=0),
    },
    'start-scheduled-matches-every-minute': {
        'task': 'tournaments.start_scheduled_matches',
        'schedule': crontab(minute='*'),
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
        'clubs': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'matches': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'tournaments': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'match_creation': {
            'handlers': ['match_creation_handler'],
            'level': 'INFO',
            'propagate': False,
        },
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
