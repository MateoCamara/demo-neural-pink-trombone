from django.urls import path
from .views import process_voice

urlpatterns = [
    path('process_voice/', process_voice, name='process_voice'),
]
