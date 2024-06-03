from django.apps import AppConfig
from .model_loader import model_loader


class VoiceappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voiceapp'

    def ready(self):
        # Esto asegura que el modelo se carga cuando la aplicación está lista
        model_loader.load_models()
        print("models loaded")
