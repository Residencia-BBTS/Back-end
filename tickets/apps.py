from django.apps import AppConfig
from .api import initialize_scheduler  


class MyAppConfig(AppConfig):
    name = 'tickets'

    def ready(self):
        initialize_scheduler()
