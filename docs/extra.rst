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