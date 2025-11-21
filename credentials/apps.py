from django.apps import AppConfig
from django.conf import settings


class CredentialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'credentials'

    def ready(self):
        import credentials.signals
