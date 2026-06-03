from django.apps import AppConfig
from .model_loader import model_loader


class VoiceappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voiceapp'

    def ready(self):
        # This makes sure the model is loaded once the application is ready
        model_loader.load_models()
        print("models loaded")
