from django.apps import AppConfig


class VerdadoretoAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'verdadoreto_app'

    def ready(self):
        import verdadoreto_app.signals  # noqa