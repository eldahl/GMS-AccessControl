from django.apps import AppConfig
#from .hardwareHandler import Coordinator

#hw_coordinator = {}

class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'
    
    def ready(self):
        #global hw_coordinator
        print("Starting NOT Hardware Coordinator...")
        #hw_coordinator = Coordinator()
