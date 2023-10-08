from django.apps import AppConfig


class HakaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'haka_app'

    def ready(self):
        import haka_app.signals
