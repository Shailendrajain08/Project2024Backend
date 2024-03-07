from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Core Application config class, need to attached this for admin to find the CoreApplication
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    
    def ready(self):
        import core.signals  # noqa
    """
    Core Application config class, need to attached this for admin to find the CoreApplication
    """