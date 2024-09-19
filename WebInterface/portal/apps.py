from django.apps import AppConfig
from .keypad_handler import KeypadHandler

keypad_handler = {}

class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'
    
    def ready(self):
        global keypad_handler
        print("Starting lock handler")
        keypad_handler = KeypadHandler()
        keypad_handler.start_keypad_handler()
