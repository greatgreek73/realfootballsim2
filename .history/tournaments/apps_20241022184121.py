from django.apps import AppConfig

class TournamentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tournaments'
    verbose_name = 'Tournaments Management'

    def ready(self):
        import tournaments.signals  # Подготовка для будущих сигналов