from django.apps import AppConfig


class LocalModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'local_model'
