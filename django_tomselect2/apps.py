"""Django application configuration."""

from django.apps import AppConfig


class TomSelect2AppConfig(AppConfig):
    """Django application configuration."""

    name = "django_tomselect2"
    verbose_name = "Django Tom Select2"

    def ready(self):
        from . import conf  # noqa
