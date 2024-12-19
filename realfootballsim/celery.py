import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realfootballsim.settings')

app = Celery('realfootballsim')

# Загружаем настройки из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем и регистрируем задачи из всех приложений Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
