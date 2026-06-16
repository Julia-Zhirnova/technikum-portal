from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """Явно импортируем admin.py после того, как admin.site заменён на CustomAdminSite."""
        # Это гарантирует, что все admin.site.register() выполнятся на CustomAdminSite
        import core.admin  # noqa


class CustomAdminConfig(AdminConfig):
    """Кастомная конфигурация админки, использующая CustomAdminSite."""
    default_site = 'core.admin_site.CustomAdminSite'  # ← Теперь из admin_site.py
    
    def ready(self):
        """Переопределяем ready(), чтобы НЕ вызывать autodiscover() автоматически."""
        # Не вызываем super().ready(), чтобы autodiscover() не вызывался здесь
        # Он будет вызван позже в CoreConfig.ready()
        pass

