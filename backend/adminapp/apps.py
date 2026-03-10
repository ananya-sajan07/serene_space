from django.apps import AppConfig

class AdminappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminapp'

    def ready(self):
        #Ensure templates are loaded
        import adminapp.templates