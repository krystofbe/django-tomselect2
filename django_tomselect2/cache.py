"""
Shared memory across multiple machines to the heavy AJAX lookups.

TomSelect2 uses django.core.cache_ to share fields across
multiple threads and even machines.

TomSelect2 uses the cache backend defined in the setting
``TOMSELECT2_CACHE_BACKEND`` [default=``default``].

It is advised to always setup a separate cache server for TomSelect2.

.. _django.core.cache: https://docs.djangoproject.com/en/dev/topics/cache/
"""

from django.core.cache import caches

from .conf import settings

__all__ = ("cache",)

cache = caches[settings.TOMSELECT2_CACHE_BACKEND]
