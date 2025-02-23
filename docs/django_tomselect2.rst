=====================================
Django Tom Select 2 Documentation
=====================================

.. note::

   This documentation describes using the `Tom Select <https://tom-select.js.org/>`_ library with Django via the
   **django-tomselect2** package. It explains how to configure, install, and use Tom Select in your Django forms, including
   advanced features such as AJAX loading (heavy widgets), model-based widgets, and more.

API Documentation
=================

Configuration
-------------
.. automodule:: django_tomselect2.conf
    :members:
    :undoc-members:
    :show-inheritance:

Widgets
-------
.. automodule:: django_tomselect2.forms
    :members:
    :undoc-members:
    :show-inheritance:

URLs
----
.. automodule:: django_tomselect2.urls
    :members:
    :undoc-members:
    :show-inheritance:

Views
-----
.. automodule:: django_tomselect2.views
    :members:
    :undoc-members:
    :show-inheritance:

Cache
-----
.. automodule:: django_tomselect2.cache
    :members:
    :undoc-members:
    :show-inheritance:

JavaScript
----------
``django-tomselect2`` automatically handles the initialization of your Tom Select fields. 
Simply include ``{{ form.media.js }}`` (and CSS if needed) in your template—ideally before 
the closing ``</body>`` tag—to ensure Tom Select is loaded and configured.

If you insert forms dynamically after page load, or you want to handle initialization 
manually, ``django-tomselect2`` also provides a convenient initialization call. For 
example, if you add elements with the class ``django-tomselect2`` on the fly, you can 
activate them like so:

.. code-block:: javascript

    /* Generic example usage */
    document.querySelectorAll('.django-tomselect2').forEach(function(el) {
        // This assumes your library JS sets up Tom Select with any
        // desired default options. If you need custom per-element
        // options, pass them here.
        const settings = JSON.parse(el.getAttribute('data-tom-select') || '{}');
        new TomSelect(el, settings);
    });

Configuration in Django
-----------------------

You can configure Tom Select globally or on individual widgets via the attributes. 
The majority of Tom Select’s options can be passed as JSON in the widget’s 
``data-tom-select`` attribute. For instance:

.. code-block:: python

    from django import forms
    from django_tomselect2.forms import TomSelectWidget

    class MyForm(forms.Form):
        my_field = forms.ChoiceField(
            widget=TomSelectWidget(
                attrs={
                    "data-tom-select": '{"placeholder": "Select an option", "maxItems": 5}'
                }
            )
        )

You can also pass options through your Django settings (``TOMSELECT2_TOM_SELECT_SETTINGS``), 
ensuring a global default configuration for all widgets. Individual widget settings will 
override these global defaults.

(See the Tom Select documentation for a full list of available options.)

Configuring Tom Select
----------------------

Similar to the example above, Tom Select can be configured either from JavaScript or from 
within Django:

- **From JavaScript** (manual initialization): Provide any valid Tom Select options directly.
- **From Django** (automatic initialization): Use the widget’s ``attrs`` or the package’s 
  global settings (``TOMSELECT2_TOM_SELECT_SETTINGS``) to pass your configuration.

Example:

.. code-block:: python

    class AnotherForm(forms.Form):
        my_multi_field = forms.MultipleChoiceField(
            widget=TomSelectWidget(
                attrs={
                    "data-tom-select": '{"plugins":["clear_button"], "hideSelected":false}',
                }
            )
        )

Security & Authentication
-------------------------
When using Tom Select with dynamic (AJAX-based) widgets, be mindful of caching 
and security. The heavy (AJAX) widgets keep a reference to their configuration in 
Django’s cache, so be sure to set up a reliable external cache (e.g., Redis or Memcached).

For private or authenticated data, you may want to protect the view endpoint. You could, 
for example, subclass the provided Ajax views and wrap them with Django’s 
``LoginRequiredMixin`` or your own permission checks:

.. code-block:: python

    from django.contrib.auth.mixins import LoginRequiredMixin
    from django_tomselect2.views import AutoResponseView

    class MyPrivateAjaxView(LoginRequiredMixin, AutoResponseView):
        pass

Then specify ``data_view`` for your widget:

.. code-block:: python

    class MyConfidentialWidget(HeavyTomSelectWidget):
        data_view = 'my-private-ajax-endpoint'
        # other widget config…

Remember that when using the heavy widgets, an attacker could spam requests to keep 
the cache populated. Isolating your ``django-tomselect2`` usage to a dedicated cache 
can mitigate any potential issues.

