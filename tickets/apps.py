from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from .api import update_tickets

class MyAppConfig(AppConfig):
    name = 'tickets'

    def ready(self):
        from .api import initialize_scheduler  # Importação tardia
        initialize_scheduler()
