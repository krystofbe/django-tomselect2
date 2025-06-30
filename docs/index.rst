.. django-tomselect2 documentation master file, created by
   sphinx-quickstart on Mon Dec 27 10:07:35 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


django-tomselect2
=================

.. image:: https://img.shields.io/pypi/v/django-tomselect2.svg
    :target: https://pypi.python.org/pypi/django-tomselect2
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/django-tomselect2.svg
    :target: https://pypi.org/project/django-tomselect2/
    :alt: Supported Python versions

.. image:: https://github.com/krystofbe/django-tomselect2/actions/workflows/test.yml/badge.svg
    :target: https://github.com/krystofbe/django-tomselect2/actions/workflows/test.yml
    :alt: Github Test Workflow Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: black

.. image:: https://img.shields.io/badge/Coverage-100%25-brightgreen
    :target: https://github.com/krystofbe/django-tomselect2/actions/workflows/test.yml
    :alt: Coverage

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit
    :alt: pre-commit

This is a Django_ integration of TomSelect_, a lightweight, vanilla JavaScript solution for enhancing ``<select>`` elements.
Tom Select is a fork of Selectize.js, focused on modern JavaScript practices, performance, and extensibility without jQuery dependency.
It provides a user-friendly interface for selecting items, with features like tagging, remote data loading, and more.

The application includes Tom Select driven Django Widgets and Form Fields.

.. _Django: https://www.djangoproject.com/
.. _TomSelect: https://tom-select.js.org/

Installation
------------

Install django-tomselect2:

.. code-block:: console

    python3 -m pip install django-tomselect2

Add django_tomselect2 to your INSTALLED_APPS in your project settings.

.. code-block:: python

    INSTALLED_APPS = [
        # other 3rd party apps…
        'django_tomselect2',
    ]

Add django_tomselect2 to your URL root configuration **if** you plan to use Model-widgets (which rely on AJAX):

.. code-block:: python

    from django.urls import include, path

    urlpatterns = [
        # other patterns…
        path("tomselect2/", include("django_tomselect2.urls")),
        # other patterns…
    ]

The Model-widgets require a **persistent** cache backend across all application servers.
This is because the widget needs to store metadata for fetching results based on user input.

**This means that the DummyCache backend will not work!**

The default cache backend is LocMemCache, which is persistent only across a single node.
For projects on a single server, this works fine, but scaling to multiple servers
will cause issues.

Below is an example setup using Redis, which works well for multi-server setups:

Make sure you have a Redis server up and running:

.. code-block:: console

    # Debian
    sudo apt-get install redis-server

    # macOS
    brew install redis

    # install Redis python client
    python3 -m pip install django-redis

Next, add the cache configuration to your settings.py as follows:

.. code-block:: python

    CACHES = {
        # ... default cache config and others
        "tomselect": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/2",  # Use a different DB for TomSelect
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    # Tell django-tomselect2 which cache configuration to use:
    TOMSELECT2_CACHE_BACKEND = "tomselect"

.. note::
    A custom timeout for your cache backend will act as an indirect session limit.
    Once the cache expires, dynamic Tom Select fields will stop working.
    It is recommended to use a dedicated cache database with a sensible
    replacement policy (LRU, FIFO, etc.).

Customizing Tom Select Assets
-----------------------------

By default, ``django-tomselect2`` includes a specific version of Tom Select JavaScript and CSS files.
However, you might want to use a different version, a CDN-hosted file, or bundle Tom Select assets
as part of your project's own asset pipeline.

**JavaScript**

To use your own Tom Select JavaScript file(s), set the ``TOMSELECT2_TOM_SELECT_JS``
setting in your Django ``settings.py``. This should be a list of strings, where each
string is a path or URL to a JavaScript file.

.. code-block:: python

    # settings.py

    # Example: Using a CDN
    # TOMSELECT2_TOM_SELECT_JS = ['https://cdnjs.cloudflare.com/ajax/libs/tom-select/2.3.1/js/tom-select.complete.min.js']

    # Example: Using a local static file
    # TOMSELECT2_TOM_SELECT_JS = ['my_custom_assets/js/tom-select.custom.js']

    # If you are bundling Tom Select JavaScript yourself (e.g., via Webpack, Rollup, etc.) and
    # do not want django-tomselect2 to include any Tom Select JS file from its defaults,
    # you can set this to an empty list:
    # TOMSELECT2_TOM_SELECT_JS = []

The default is: ``["tom-select/js/tom-select.complete.min.js"]``

**CSS**

To use your own Tom Select CSS file, set the ``TOMSELECT2_TOM_SELECT_THEME_CSS_TEMPLATE``
setting in your Django ``settings.py``. This is a string that can be a direct path/URL
to your CSS file or a template string containing ``{theme}`` if you wish to support
dynamic theming based on the ``TOMSELECT2_THEME`` setting (default theme is "default").

.. code-block:: python

    # settings.py

    # Example: Using a CDN for a specific theme (e.g., bootstrap5)
    # TOMSELECT2_TOM_SELECT_THEME_CSS_TEMPLATE = 'https://cdnjs.cloudflare.com/ajax/libs/tom-select/2.3.1/css/tom-select.bootstrap5.min.css'
    # TOMSELECT2_THEME = "bootstrap5" # Ensure this matches if your CSS is theme-specific

    # Example: Using a local static file (if your path doesn't use {theme})
    # TOMSELECT2_TOM_SELECT_THEME_CSS_TEMPLATE = 'my_custom_assets/css/tom-select.custom.css'

    # If you are bundling Tom Select CSS yourself and do not want django-tomselect2 to include
    # any Tom Select theme CSS file from its defaults, you can set this to an empty string:
    # TOMSELECT2_TOM_SELECT_THEME_CSS_TEMPLATE = ""

The default is: ``"tom-select/css/tom-select.{theme}.min.css"``

.. note::
    ``django-tomselect2`` also includes its own small JavaScript file (``django_tomselect2/django_tomselect.js``)
    and CSS file (``django_tomselect2/django_tomselect.css``) for the Django integration logic
    (e.g., initializing the widgets, handling dependent fields, HTMX support).
    The settings above control the core Tom Select library assets, not these integration-specific files.
    These integration files will still be included by default via the widget's ``media`` property,
    as they are essential for the widgets to function correctly with Django and HTMX.
    If you set ``TOMSELECT2_TOM_SELECT_JS = []`` and ``TOMSELECT2_TOM_SELECT_THEME_CSS_TEMPLATE = ""``,
    the core Tom Select library assets will be omitted, but the integration assets will remain.

HTMX Integration
----------------

``django-tomselect2`` provides out-of-the-box integration with HTMX_ for a smoother experience with dynamic content.

-   **Automatic Initialization**: Tom Select widgets within content loaded or swapped into the DOM by HTMX (via the ``htmx:load`` event, which is an alias for ``htmx:afterSwap``) will be automatically initialized.
-   **Event Triggering**: When a Tom Select widget's value changes, ``django-tomselect2`` will automatically fire a standard ``change`` event on the underlying ``<select>`` element. This allows HTMX to listen for these changes using triggers like ``hx-trigger="change"``.
-   **Dependent Fields**: The HTMX integration also works seamlessly with dependent field logic. When a parent field changes, dependent Tom Select fields will be updated, even if they are part of an HTMX-swapped fragment.

To leverage this, ensure that:
1.  HTMX is loaded on your page.
2.  The ``{{ form.media.js }}`` (which includes ``django_tomselect2/django_tomselect.js`` and your chosen Tom Select JS) and ``{{ form.media.css }}`` are present in your base template or relevant HTMX-rendered templates, so the necessary JavaScript is available when HTMX swaps content.

No special configuration is needed in ``django-tomselect2`` to enable this; it's active by default if HTMX is detected on the page (``window.htmx``).

.. _HTMX: https://htmx.org/

External Dependencies
---------------------

-  jQuery is **not** required by Tom Select itself, which is vanilla JavaScript.
   ``django-tomselect2`` also does not require jQuery.


Quick Start
-----------

Here is a quick example to get you started:

First, ensure you followed the installation instructions above.
Once everything is set up, let's look at a simple example.

We have the following model:

.. code-block:: python

    # models.py
    from django.conf import settings
    from django.db import models

    class Book(models.Model):
        author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        co_authors = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            related_name='co_authored_by'
        )


Next, we create a model form with custom Tom Select widgets.

.. code-block:: python

    # forms.py
    from django import forms
    from django_tomselect2 import forms as ts2forms
    from . import models
    from django.contrib.auth import get_user_model

    User = get_user_model()

    class AuthorWidget(ts2forms.ModelTomSelectWidget):
        # queryset = User.objects.all()
        search_fields = [
            "username__icontains",
            "email__icontains",
        ]

    class CoAuthorsWidget(ts2forms.ModelTomSelectMultipleWidget):
        # queryset = User.objects.all()
        search_fields = [
            "username__icontains",
            "email__icontains",
        ]

    class BookForm(forms.ModelForm):
        class Meta:
            model = models.Book
            fields = "__all__"
            widgets = {
                "author": AuthorWidget,
                "co_authors": CoAuthorsWidget,
            }


A simple class-based view to render your form:

.. code-block:: python

    # views.py
    from django.views import generic
    from . import forms, models
    from django.urls import reverse_lazy

    class BookCreateView(generic.CreateView):
        model = models.Book
        form_class = forms.BookForm
        success_url = reverse_lazy("book-create")


Make sure to add the view to your urls.py:

.. code-block:: python

    # urls.py
    from django.urls import path
    from . import views

    urlpatterns = [
        # other patterns for your app
        path("book/create/", views.BookCreateView.as_view(), name="book-create"),
    ]

    # Ensure your project's root urls.py includes tomselect2 and your app's URLs:
    # from django.contrib import admin
    # from django.urls import path, include
    #
    # urlpatterns = [
    #     path("admin/", admin.site.urls),
    #     path("tomselect2/", include("django_tomselect2.urls")),
    #     path("myapp/", include("myapp.urls")),
    # ]


Finally, we need a simple template, for example, ``myapp/templates/myapp/book_form.html``:

.. code-block:: html

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Create Book</title>
        {{ form.media.css }}
        <style>
            body { font-family: sans-serif; margin: 20px; }
            .form-row { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input[type="text"], select, .ts-wrapper {
                width: 100%;
                box-sizing: border-box;
            }
            .ts-wrapper { min-height: 38px; }
        </style>
    </head>
    <body>
        <h1>Create a new Book</h1>
        <form method="POST">
            {% csrf_token %}
            {% for field in form %}
                <div class="form-row">
                    {{ field.label_tag }}
                    {{ field }}
                    {% if field.help_text %}
                        <small style="display: block;">{{ field.help_text }}</small>
                    {% endif %}
                    {% for error in field.errors %}
                        <p style="color: red;">{{ error }}</p>
                    {% endfor %}
                </div>
            {% endfor %}
            <input type="submit" value="Submit">
        </form>
        {{ form.media.js }}
        <!-- If you are using HTMX, ensure htmx.min.js is loaded -->
        <!-- <script src="https://unpkg.com/htmx.org@1.9.9" integrity="sha384-QFjmbokDn2DjBjq+fM+8LUIVrAgqcNW2s0PjAxHETgRn9l4fvX31ZxDxvwQnyMOX" crossorigin="anonymous"></script> -->
    </body>
    </html>

Done—enjoy the wonders of Tom Select!


Changelog
---------

See Github releases:
https://github.com/krystofbe/django-tomselect2/releases



All Contents
============

Contents:

.. toctree::
   :maxdepth: 2
   :glob:

   django_tomselect2
   extra
   CONTRIBUTING

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
