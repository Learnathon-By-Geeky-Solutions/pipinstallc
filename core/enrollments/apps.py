from django.apps import AppConfig


class EnrollmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'enrollments'
    label = 'core_enrollments'
    verbose_name = 'Enrollments'

    def ready(self):
        """
        Import signal handlers when Django starts
        This ensures that our enrollment signals are connected
        """
        import enrollments.signals  # This will import signals.py
