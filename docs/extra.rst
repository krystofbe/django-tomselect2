Extra
=====

Chained Tom Select
------------------

Suppose you have an address form where a user should choose a Country and a City.
When the user selects a country, we want to show only the cities belonging to that country.
Hence, one selector depends on another one.

.. note::
    Does not work with the 'light' version (django_tomselect2.forms.TomSelectWidget),
    because all options for the dependent field would need to be preloaded.

Heavy Widget Auto-Loading
-------------------------

Starting from version 0.1.0, Heavy widgets automatically load initial results when the dropdown is opened,
providing a better user experience similar to standard HTML select elements.

Default Behavior
````````````````

By default, Heavy widgets now:

- Load initial results when the dropdown is focused/opened (``preload: 'focus'``)
- Allow empty search queries to fetch results (``shouldLoad`` returns true for empty queries)
- Display up to 25 results initially (configurable via ``max_results``)

This means users see available options immediately upon clicking the widget, without needing to type first.

Configuring Preload Behavior
`````````````````````````````

You can customize or disable this behavior using ``tom_select_settings``:

.. code-block:: python

    # Default behavior - loads on focus
    widget = ModelTomSelectWidget(
        data_view="author_autocomplete"
    )

    # Disable preload (old behavior - require typing)
    widget = ModelTomSelectWidget(
        data_view="author_autocomplete",
        tom_select_settings={
            'preload': False,
            'minLength': 1  # Require at least 1 character
        }
    )

    # Load immediately on widget initialization
    widget = ModelTomSelectWidget(
        data_view="author_autocomplete",
        tom_select_settings={'preload': True}
    )

    # Customize number of initial results
    widget = ModelTomSelectWidget(
        data_view="author_autocomplete",
        max_results=10  # Show only 10 results initially
    )

Models
``````

Here are our two models:

.. code-block:: python

    class Country(models.Model):
        name = models.CharField(max_length=255)


    class City(models.Model):
        name = models.CharField(max_length=255)
        country = models.ForeignKey('Country', related_name="cities", on_delete=models.CASCADE)


Customizing a Form
``````````````````

Let's link two widgets via a *dependent_fields* dictionary. The key represents the name of
the field in the form. The value represents the name of the field in the model (used in `queryset`).

.. code-block:: python
    :emphasize-lines: 17

    from django import forms
    from django_tomselect2.forms import ModelTomSelectWidget

    class AddressForm(forms.Form):
        country = forms.ModelChoiceField(
            queryset=Country.objects.all(),
            label="Country",
            widget=ModelTomSelectWidget(
                model=Country,
                search_fields=['name__icontains'],
            )
        )

        city = forms.ModelChoiceField(
            queryset=City.objects.all(),
            label="City",
            widget=ModelTomSelectWidget(
                model=City,
                search_fields=['name__icontains'],
                dependent_fields={'country': 'country'},
                max_results=500,
            )
        )


Interdependent Tom Select
-------------------------

You may also want to avoid forcing the user to select one field first.
Instead, you want to allow the user to choose any field, and then the other Tom Select
widgets update accordingly.

.. code-block:: python
    :emphasize-lines: 7

    from django import forms
    from django_tomselect2.forms import ModelTomSelectWidget

    class AddressForm(forms.Form):
        country = forms.ModelChoiceField(
            queryset=Country.objects.all(),
            label="Country",
            widget=ModelTomSelectWidget(
                search_fields=['name__icontains'],
                dependent_fields={'city': 'cities'},
            )
        )

        city = forms.ModelChoiceField(
            queryset=City.objects.all(),
            label="City",
            widget=ModelTomSelectWidget(
                search_fields=['name__icontains'],
                dependent_fields={'country': 'country'},
                max_results=500,
            )
        )

Note how the ``country`` widget has ``dependent_fields={'city': 'cities'}``, using the
model’s related name ``cities`` rather than the form field name ``city``.

.. caution::
    Be aware of using interdependent Tom Select fields in a parent-child relation.
    Once a child is selected, changing the parent might be constrained (sometimes only one value
    remains available). You may want to prompt the user to reset the child field first, so that
    the parent is fully selectable again.


Multi-dependent Tom Select
--------------------------

Finally, you may want to filter options based on two or more Tom Select fields (some code is
omitted for brevity):

.. code-block:: python
    :emphasize-lines: 14

    from django import forms
    from django_tomselect2.forms import ModelTomSelectWidget

    class SomeForm(forms.Form):
        field1 = forms.ModelChoiceField(
            widget=ModelTomSelectWidget(
                # model, search_fields, etc.
            )
        )

        field2 = forms.ModelChoiceField(
            widget=ModelTomSelectWidget(
                # model, search_fields, etc.
            )
        )

        field3 = forms.ModelChoiceField(
            widget=ModelTomSelectWidget(
                dependent_fields={'field1': 'field1', 'field2': 'field2'},
            )
        )

In this setup, when you change ``field1`` or ``field2,`` the set of available choices
in ``field3`` is automatically updated according to their values.
