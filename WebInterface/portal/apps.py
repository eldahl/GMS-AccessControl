from django.apps import AppConfig
from .lock_handler import LockHandler

lock_handler = {}

class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'
    
    def ready(self):
        global lock_handler
        print("Starting lock handler")
        lock_handler = LockHandler()
        lock_handler.start_lock_handler()
