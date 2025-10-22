from django.apps import AppConfig


class CdmisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CDMIS'
from django.apps import AppConfig

class CDMISConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CDMIS'

    def ready(self):
        import CDMIS.signals