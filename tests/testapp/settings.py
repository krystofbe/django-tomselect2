import os.path

import django

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django_tomselect2",
    "tests.testapp",
)

STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

SITE_ID = 1
ROOT_URLCONF = "tests.testapp.urls"

LANGUAGES = [
    ("de", "German"),
    ("en", "English"),
]
LANGUAGE_CODE = "en"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": ["templates"],
    },
]

SECRET_KEY = "123456"  # noqa: S105

if django.VERSION < (4, 0):
    USE_L10N = True
USE_I18N = True
USE_TZ = True
