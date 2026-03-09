from django.apps import AppConfig


class WmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wms'

    def ready(self):
        """
        Called once when Django starts up.
        Starts the background thread that pulls from Google Sheets every 2 minutes.
        """
        import os
        # Only run in the main process, not in Django's reloader subprocess
        if os.environ.get('RUN_MAIN') != 'true':
            return
        from .sheets_sync import start_background_sync
        start_background_sync()
