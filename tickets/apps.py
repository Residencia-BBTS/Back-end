from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'tickets'

    def ready(self):
        from .api import initialize_scheduler  
        initialize_scheduler()
