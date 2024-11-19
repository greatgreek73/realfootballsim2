import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')

app = Celery('realfootballsim')

# Загружаем настройки из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Настраиваем периодические задачи
app.conf.beat_schedule = {
    # Симуляция матчей (каждую минуту)
    'simulate-matches': {
        'task': 'tournaments.check_and_simulate_matches',
        'schedule': crontab(),  # каждую минуту
    },
    # Проверка окончания сезона (каждый день в полночь)
    'check-season-end': {
        'task': 'tournaments.check_season_end',
        'schedule': crontab(minute=0, hour=0),  # в 00:00
    }
}

# Автоматически обнаруживаем и регистрируем задачи из всех приложений Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')