from django.apps import AppConfig
from .coordinator import Coordinator

hw_coordinator = {}

class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'
    
    def ready(self):
        global hw_coordinator
        print("Starting Hardware Coordinator...")
        hw_coordinator = Coordinator()
        hw_coordinator.start_coordinator()
