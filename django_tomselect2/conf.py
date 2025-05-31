"""Settings for django-tomselect2."""

from appconf import AppConf
from django.conf import settings

__all__ = ("TomSelect2Conf", "settings")


class TomSelect2Conf(AppConf):
    """Settings for django-tomselect2."""

    CACHE_BACKEND = "default"
    """
    TomSelect uses Django's cache to ensure a consistent state across multiple machines.

    Example of settings.py::

        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/1",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                }
            },
            'tomselect': {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/2",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                }
            }
        }

        # Set the cache backend to tomselect
        TOMSELECT2_CACHE_BACKEND = 'tomselect'

    .. tip:: To ensure a consistent state across all your machines, use
        a consistent external cache backend like Memcached, Redis, or a database.

    .. note::
        If you've copied the example configuration, ensure that Redis is set up.
        It's recommended to run a separate Redis server in a production environment.

    .. note:: The timeout of TomSelect's caching backend determines
        how long a browser session can last.
        Once the widget is dropped from the cache, the JSON response view will return a 404.
    """
    CACHE_PREFIX = "tomselect_"
    """
    If your caching backend does not support multiple databases,
    you can isolate TomSelect using the cache prefix setting.
    The default is set to `tomselect_`, which can be changed if needed.
    """

    TOM_SELECT_JS = ["tom-select/js/tom-select.complete.min.js"]
    """
    List of JavaScript files for Tom Select.

    Defaults to using local static files. Users can override this in their
    `settings.py` to use different versions or CDN links.

    Example::

        TOM_SELECT_JS = [
            'https://your.cdn.com/tom-select.min.js',
            'path/to/your/custom-script.js',
        ]

    .. tip:: Change this setting to a local asset in your development environment to
        develop without an Internet connection.
    """

    TOM_SELECT_THEME_CSS_TEMPLATE = "tom-select/css/tom-select.{theme}.min.css"
    """
    Template string for Tom Select theme CSS files.
    The `{theme}` placeholder will be replaced with the configured `THEME`.

    Example::

        TOM_SELECT_THEME_CSS_TEMPLATE = "tom-select/css/tom-select.bootstrap4.min.css"

    .. tip:: Use this template to define custom theme paths based on the selected theme.
    """

    THEME = "default"
    """
    TomSelect supports custom themes using the theme option so you can style TomSelect
    to match the rest of your application.

    .. tip:: When using other themes, ensure you provide the corresponding CSS using
        `TOM_SELECT_THEME_CSS_TEMPLATE`.
    """

    JSON_ENCODER = "django.core.serializers.json.DjangoJSONEncoder"
    """
    A :class:`JSONEncoder<json.JSONEncoder>` used to generate the API response for the model widgets.

    A custom JSON encoder might be useful when your models use
    a special primary key that isn't serializable by the default encoder.
    """

    TOM_SELECT_SETTINGS = {}
    """
    Global Tom Select settings applied to all widgets.

    Example::

        TOM_SELECT_SETTINGS = {
            "maxItems": 2,
            "plugins": ["no_active_items"],
        }

    .. tip:: These settings can be overridden locally for individual widgets if needed.
    """

    class Meta:
        """Prefix for all django-tomselect2 settings."""

        prefix = "TOMSELECT2"
