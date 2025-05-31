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

Add django_tomselect2 to your URL root configuration:

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
            "LOCATION": "redis://127.0.0.1:6379/2",
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


External Dependencies
---------------------

-  jQuery is **not** required by Tom Select itself, but if you have existing scripts
   or transitional code using jQuery, make sure to load it before your form JS
   if needed. By default, Tom Select is purely vanilla JavaScript.


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

    class AuthorWidget(ts2forms.ModelTomSelectWidget):
        search_fields = [
            "username__icontains",
            "email__icontains",
        ]

    class CoAuthorsWidget(ts2forms.ModelTomSelectMultipleWidget):
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

    class BookCreateView(generic.CreateView):
        model = models.Book
        form_class = forms.BookForm
        success_url = "/"


Make sure to add the view to your urls.py:

.. code-block:: python

    # urls.py
    from django.urls import include, path
    from . import views

    urlpatterns = [
        # other patterns
        path("tomselect2/", include("django_tomselect2.urls")),
        # other patterns
        path("book/create", views.BookCreateView.as_view(), name="book-create"),
    ]


Finally, we need a simple template, myapp/templates/myapp/book_form.html:

.. code-block:: html

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Create Book</title>
        {{ form.media.css }}
        <style>
            input, select {
                width: 100%;
            }
        </style>
    </head>
    <body>
        <h1>Create a new Book</h1>
        <form method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit" value="Submit">
        </form>
        {{ form.media.js }}
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
