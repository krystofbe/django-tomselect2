"""
django-tomselect2 Widgets.

These components are responsible for rendering
the necessary HTML data markups. Since this whole
package is to render choices using Tom Select JavaScript
library, hence these components are meant to be used
with choice fields.

Widgets are generally of tree types:
Light, Heavy and Model.

Light
~~~~~

They are not meant to be used when there
are too many options, say, in thousands.
This is because all those options would
have to be pre-rendered onto the page
and JavaScript would be used to search
through them. Said that, they are also one
the easiest to use. They are a
drop-in-replacement for Django's default
select widgets.

Heavy
~~~~~

They are suited for scenarios when the number of options
are large and need complex queries (from maybe different
sources) to get the options.

This dynamic fetching of options undoubtedly requires
Ajax communication with the server. django-tomselect2 includes
a helper JS file which is included automatically,
so you need not worry about writing any Ajax related JS code.
Although on the server side you do need to create a view
specifically to respond to the queries.

Model
~~~~~

Model-widgets are a further specialized versions of Heavies.
These do not require views to serve Ajax requests.
When they are instantiated, they register themselves
with one central view which handles Ajax requests for them.

Heavy and Model widgets have respectively the word 'Heavy' and 'Model' in
their name.  Light widgets are normally named, i.e. there is no 'Light' word
in their names.

.. inheritance-diagram:: django_tomselect2.forms
    :parts: 1

"""

import json
import operator
import uuid
from contextlib import suppress
from functools import reduce
from pickle import PicklingError  # nosec

import django
from django import forms
from django.core import signing
from django.db.models import Q
from django.forms.models import ModelChoiceIterator
from django.urls import reverse

from .cache import cache
from .conf import settings

if django.VERSION < (4, 0):
    from django.contrib.admin.utils import (
        lookup_needs_distinct as lookup_spawns_duplicates,
    )
else:
    from django.contrib.admin.utils import lookup_spawns_duplicates


class TomSelectMixin:
    """
    The base mixin for integrating Tom Select with Django widgets.
    """

    theme = settings.TOMSELECT2_THEME
    empty_label = ""
    plugins = {}

    def __init__(
        self, attrs=None, choices=(), plugins=None, tom_select_settings=None, **kwargs
    ):
        """
        Initialize TomSelectMixin.

        Args:
            attrs (dict): HTML attributes for the widget.
            choices (iterable): Choices for the select widget.
            plugins (dict): Plugins and their configurations.
            tom_select_settings (dict): Custom Tom Select settings for this widget.
            theme (str): Theme name for Tom Select.
        """
        super().__init__(attrs)
        self.theme = kwargs.pop("theme", self.theme)
        self.plugins = plugins or self.plugins  # Use provided plugins or default
        self.tom_select_settings = tom_select_settings or {}

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add common Tom Select attributes that apply to all widget types."""
        # Merge base_attrs with self.attrs
        base_attrs = base_attrs or {}
        merged_attrs = {**self.attrs, **base_attrs}

        existing_settings = {}
        if "data-tom-select" in merged_attrs:
            with suppress(json.JSONDecodeError, TypeError):
                existing_settings = json.loads(merged_attrs["data-tom-select"])

        # Start with global settings
        tom_select_settings = settings.TOMSELECT2_TOM_SELECT_SETTINGS.copy()

        # Update with existing settings from the attributes
        tom_select_settings.update(existing_settings)

        # Update with per-widget settings
        tom_select_settings.update(self.tom_select_settings)

        # Common settings that apply to all widget types
        tom_select_settings.update(
            {
                "theme": self.theme,
                "placeholder": merged_attrs.get("placeholder", "")
                if extra_attrs
                else merged_attrs.get("placeholder", ""),
            }
        )

        # Process plugins
        if self.plugins:
            tom_select_settings["plugins"] = self.plugins

        # Serialize the settings to JSON
        default_attrs = {
            "data-tom-select": json.dumps(tom_select_settings),
            "data-placeholder": self.empty_label,
        }

        # Merge other attributes from the parent class base_attrs but not data-tom-select
        default_attrs.update(
            {k: v for k, v in merged_attrs.items() if k != "data-tom-select"}
        )

        return super().build_attrs(default_attrs, extra_attrs=extra_attrs)

    def optgroups(self, name, value, attrs=None):
        """
        Optionally add an empty choice for clearable selects.

        Args:
            name (str): Field name.
            value (str): Current value.
            attrs (dict): HTML attributes.

        Returns:
            list: Option groups.
        """
        if not self.is_required and not self.allow_multiple_selected:
            self.choices = [("", self.empty_label or "---------")] + list(self.choices)
        return super().optgroups(name, value, attrs=attrs)

    @property
    def media(self):
        """
        Define the media (CSS and JS) required by Tom Select.

        Returns:
            forms.Media: Media object containing JS and CSS files.
        """
        tom_select_js = settings.TOMSELECT2_TOM_SELECT_JS

        theme_css = settings.TOMSELECT2_TOM_SELECT_THEME_CSS_TEMPLATE.format(
            theme=self.theme
        )

        return forms.Media(
            js=tom_select_js + ["django_tomselect2/django_tomselect.js"],
            css={
                "all": [
                    "django_tomselect2/django_tomselect.css",
                    theme_css,
                ]
            },
        )


class TomSelectTagMixin(TomSelectMixin):
    """Mixin to add tom-select tag functionality."""

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add tom-select's tag attributes."""
        # Call the parent build_attrs to get existing attributes
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)

        # Load existing tom-select settings from data-tom-select
        tom_select_settings = json.loads(attrs.get("data-tom-select", "{}"))

        # Update settings to enable tagging functionality
        tom_select_settings.update(
            {
                "create": True,  # Allow creation of new tags
                "delimiter": ",",  # Delimiter for separating tags
                "persist": False,  # Do not persist created tags in the options
                "dropdownParent": "body",  # Optional: Append dropdown to body
                "placeholder": extra_attrs.get("placeholder", "Select or add tags")
                if extra_attrs
                else "Select or add tags",
                "hideSelected": False,  # Show selected items in the dropdown
            }
        )

        # Serialize the updated settings back to JSON
        attrs["data-tom-select"] = json.dumps(tom_select_settings)

        return attrs


class TomSelectWidget(TomSelectMixin, forms.Select):
    """
    Tom Select drop-in widget.

    Example usage::

        class MyModelForm(forms.ModelForm):
            class Meta:
                model = MyModel
                fields = ('my_field', )
                widgets = {
                    'my_field': TomSelectWidget
                }

    or::

        class MyForm(forms.Form):
            my_choice = forms.ChoiceField(widget=TomSelectWidget)

    """


class TomSelectMultipleWidget(TomSelectMixin, forms.SelectMultiple):
    """
    Tom Select drop-in widget for multiple select.

    Works just like :class:`.TomSelectWidget` but for multi select.
    """


class TomSelectTagWidget(TomSelectTagMixin, TomSelectMixin, forms.SelectMultiple):
    """
    Tom Select drop in widget with tagging support. It allows to dynamically create new options from text input by the user.

    Example for :class:`.django.contrib.postgres.fields.ArrayField`::

        class MyWidget(TomSelectTagWidget):

            def value_from_datadict(self, data, files, name):
                values = super().value_from_datadict(data, files, name)
                return ",".join(values)

            def optgroups(self, name, value, attrs=None):
                values = value[0].split(',') if value[0] else []
                selected = set(values)
                subgroup = [self.create_option(name, v, v, selected, i) for i, v in enumerate(values)]
                return [(None, subgroup, 0)]

    """


class HeavyTomSelectMixin(forms.Widget):
    """Mixin that adds Tom Select's AJAX options and registers itself on Django's cache."""

    dependent_fields = {}
    data_view = None
    data_url = None
    theme = settings.TOMSELECT2_THEME

    def __init__(self, attrs=None, choices=(), **kwargs):
        """
        Initialize HeavyTomSelectMixin.

        Args:
            data_view (str): URL pattern name for AJAX.
            data_url (str): Direct URL for AJAX.
            dependent_fields (dict): Dependent parent fields.
        """
        super().__init__(attrs, choices, **kwargs)

        self.uuid = str(uuid.uuid4())
        self.field_id = signing.dumps(self.uuid)
        self.data_view = kwargs.pop("data_view", self.data_view)
        self.data_url = kwargs.pop("data_url", self.data_url)
        self.theme = kwargs.pop("theme", self.theme)

        dependent_fields = kwargs.pop("dependent_fields", None)
        if dependent_fields is not None:
            self.dependent_fields = dict(dependent_fields)
        if not (self.data_view or self.data_url):
            raise ValueError('You must either specify "data_view" or "data_url".')

    def get_url(self):
        """Return URL from instance or by reversing :attr:`.data_view`."""
        if self.data_url:
            return self.data_url
        return reverse(self.data_view)

    def build_attrs(self, base_attrs, extra_attrs=None):
        default_attrs = {
            "data-tom-select": json.dumps(
                {
                    "searchField": ["text"],  # Adjust based on your data
                }
            ),
            "data-field_id": self.field_id,
            "data-url": self.get_url(),
            "data-widget-type": "heavy",
        }
        if self.dependent_fields:
            default_attrs["data-dependent-fields"] = " ".join(
                self.dependent_fields.keys()
            )

        default_attrs.update(base_attrs)
        return super().build_attrs(default_attrs, extra_attrs=extra_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        """Render widget and register it in Django's cache."""
        output = super().render(name, value, attrs, renderer)
        self.set_to_cache()
        return output

    def _get_cache_key(self):
        return f"{settings.TOMSELECT2_CACHE_PREFIX}{self.uuid}"

    def set_to_cache(self):
        """
        Add widget object to Django's cache.

        Override this method to serialize necessary information.
        """
        try:
            cache.set(self._get_cache_key(), {"widget": self, "url": self.get_url()})
        except (PicklingError, AttributeError) as err:
            msg = 'You need to overwrite "set_to_cache" or ensure that %s is serialisable.'
            raise NotImplementedError(msg % self.__class__.__name__) from err


class HeavyTomSelectWidget(HeavyTomSelectMixin, TomSelectWidget):
    """
    Tom Select widget with AJAX support that registers itself to Django's Cache.

    Usage example::

        class MyWidget(HeavyTomSelectWidget):
            data_view = 'my_view_name'

    or::

        class MyForm(forms.Form):
            my_field = forms.ChoiceField(
                widget=HeavyTomSelectWidget(
                    data_url='/url/to/json/response'
                )
            )

    """


class HeavyTomSelectMultipleWidget(HeavyTomSelectMixin, TomSelectMultipleWidget):
    """Tom Select multi select widget similar to :class:`.HeavyTomSelectWidget`."""


class HeavyTomSelectTagWidget(HeavyTomSelectMixin, TomSelectTagWidget):
    """Tom Select tag widget."""


# Auto Heavy widgets
class ModelTomSelectMixin:
    """
    Widget mixin that provides attributes and methods for integrating with Tom Select.

    This mixin configures the widget to work with Tom Select by setting the necessary
    data attributes and handling AJAX requests for dynamic option loading.

    .. tip:: The ModelTomSelect(Multiple)Widget will try
        to get the QuerySet from the field's choices.
        Therefore, you don't need to define a QuerySet
        if you simply apply the widget to a ForeignKey field.
    """

    model = None
    queryset = None
    search_fields = []

    """
    Model lookups that are used to filter the QuerySet.

    Example::

        search_fields = [
                'title__icontains',
            ]
    """

    max_results = 25
    """Maximal results returned by :class:`.AutoResponseView`."""

    @property
    def empty_label(self):
        if isinstance(self.choices, ModelChoiceIterator):
            return self.choices.field.empty_label
        return ""

    def __init__(self, *args, **kwargs):
        """
        Overwrite class parameters if passed as keyword arguments.

        Args:
            model (django.db.models.Model): Model to select choices from.
            queryset (django.db.models.query.QuerySet): QuerySet to select choices from.
            search_fields (list): List of model lookup strings.
            max_results (int): Max. JsonResponse view page size.
            theme (str): Theme name for Tom Select.
        """
        self.model = kwargs.pop("model", self.model)
        self.queryset = kwargs.pop("queryset", self.queryset)
        self.search_fields = kwargs.pop("search_fields", self.search_fields)
        self.max_results = kwargs.pop("max_results", self.max_results)
        defaults = {
            "data_view": "django_tomselect2:auto-json",
        }
        defaults.update(kwargs)
        super().__init__(*args, **defaults)

    def set_to_cache(self):
        """
        Add widget's attributes to Django's cache.

        Split the QuerySet to avoid pickling the entire result set.
        """
        queryset = self.get_queryset()
        cache.set(
            self._get_cache_key(),
            {
                "queryset": [queryset.none(), queryset.query],
                "cls": self.__class__,
                "search_fields": tuple(self.search_fields),
                "max_results": int(self.max_results),
                "url": str(self.get_url()),
                "dependent_fields": dict(self.dependent_fields),
                "theme": self.theme,  # Add theme to the cache
            },
        )

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        """
        Return QuerySet filtered by search_fields matching the passed term.

        Args:
            request (django.http.request.HttpRequest): The request from the widget.
            term (str): Search term.
            queryset (django.db.models.query.QuerySet): QuerySet to select choices from.
            **dependent_fields: Dependent fields and their values.

        Returns:
            QuerySet: Filtered QuerySet.
        """
        if queryset is None:
            queryset = self.get_queryset()
        search_fields = self.get_search_fields()
        select = Q()

        use_distinct = False
        if search_fields and term:
            for bit in term.split():
                or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in search_fields]
                select &= reduce(operator.or_, or_queries)
            or_queries = [Q(**{orm_lookup: term}) for orm_lookup in search_fields]
            select |= reduce(operator.or_, or_queries)
            use_distinct |= any(
                lookup_spawns_duplicates(queryset.model._meta, search_spec)
                for search_spec in search_fields
            )

        if dependent_fields:
            select &= Q(**dependent_fields)

        use_distinct |= any(
            lookup_spawns_duplicates(queryset.model._meta, search_spec)
            for search_spec in dependent_fields
        )

        if use_distinct:
            return queryset.filter(select).distinct()
        return queryset.filter(select)

    def get_queryset(self):
        """
        Return QuerySet based on :attr:`.queryset` or :attr:`.model`.

        Returns:
            QuerySet: QuerySet of available choices.
        """
        if self.queryset is not None:
            queryset = self.queryset
        elif hasattr(self.choices, "queryset"):
            queryset = self.choices.queryset
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise NotImplementedError(
                f"{self.__class__.__name__} is missing a QuerySet. Define "
                f"{self.__class__.__name__}.model, {self.__class__.__name__}.queryset, or override "
                f"{self.__class__.__name__}.get_queryset()."
            )
        return queryset

    def get_search_fields(self):
        """Return list of lookup names."""
        if self.search_fields:
            return self.search_fields
        raise NotImplementedError(
            f'{self.__class__.__name__}, must implement "search_fields".'
        )

    def optgroups(self, name, value, attrs=None):
        """
        Return only selected options and set QuerySet from `ModelChoicesIterator`.

        Args:
            name (str): Field name.
            value (str): Current value.
            attrs (dict): HTML attributes.

        Returns:
            list: Option groups.
        """
        default = (None, [], 0)
        groups = [default]
        has_selected = False
        selected_choices = {str(v) for v in value}
        if not self.is_required and not self.allow_multiple_selected:
            default[1].append(self.create_option(name, "", "", False, 0))
        if not isinstance(self.choices, ModelChoiceIterator):
            return super().optgroups(name, value, attrs=attrs)
        selected_choices = {
            c for c in selected_choices if c not in self.choices.field.empty_values
        }
        field_name = self.choices.field.to_field_name or "pk"
        query = Q(**{f"{field_name}__in": selected_choices})
        for obj in self.choices.queryset.filter(query):
            option_value = self.choices.choice(obj)[0]
            option_label = self.label_from_instance(obj)

            selected = str(option_value) in value and (
                has_selected is False or self.allow_multiple_selected
            )
            if selected is True and has_selected is False:
                has_selected = True
            index = len(default[1])
            subgroup = default[1]
            subgroup.append(
                self.create_option(
                    name, option_value, option_label, selected_choices, index
                )
            )
        return groups

    def label_from_instance(self, obj):
        """
        Return option label representation from instance.

        Can be overridden to change the representation of each choice.

        Example usage::

            class MyWidget(ModelTomSelectWidget):
                def label_from_instance(obj):
                    return str(obj.title).upper()

        Args:
            obj (django.db.models.Model): Instance of Django Model.

        Returns:
            str: Option label.
        """
        return str(obj)

    def result_from_instance(self, obj, request):
        """
        Return a dictionary representing the object.

        Can be overridden to change the result returned by
        :class:`.AutoResponseView` for each object.

        Args:
            obj (django.db.models.Model): Instance of Django Model.
            request (django.http.request.HttpRequest): The request sent to the view.

        Returns:
            dict: Representation of the object for Tom Select.
        """
        return {"id": obj.pk, "text": self.label_from_instance(obj)}


class ModelTomSelectWidget(ModelTomSelectMixin, HeavyTomSelectWidget):
    """
    Tom Select drop in model select widget.

    Example usage::

        class MyWidget(ModelTomSelectWidget):
            search_fields = [
                'title__icontains',
            ]

        class MyModelForm(forms.ModelForm):
            class Meta:
                model = MyModel
                fields = ('my_field', )
                widgets = {
                    'my_field': MyWidget,
                }

    or::

        class MyForm(forms.Form):
            my_choice = forms.ChoiceField(
                widget=ModelTomSelectWidget(
                    model=MyOtherModel,
                    search_fields=['title__icontains'],
                    theme="bootstrap5"
                )
            )

    .. tip:: The ModelTomSelect(Multiple)Widget will try
        to get the QuerySet from the fields choices.
        Therefore you don't need to define a QuerySet,
        if you just drop in the widget for a ForeignKey field.
    """


class ModelTomSelectMultipleWidget(ModelTomSelectMixin, HeavyTomSelectMultipleWidget):
    """
    Tom Select drop in model multiple select widget.

    Works just like :class:`.ModelTomSelectWidget` but for multi select.
    """


class ModelTomSelectTagWidget(ModelTomSelectMixin, HeavyTomSelectTagWidget):
    """
    Tom Select model widget with tag support.

    This it not a simple drop in widget.
    It requires to implement you own :func:`.value_from_datadict`
    that adds missing tags to you QuerySet.

    Example::

        class MyModelTomSelectTagWidget(ModelTomSelectTagWidget):
            queryset = MyModel.objects.all()

            def value_from_datadict(self, data, files, name):
                '''Create objects for given non-pimary-key values. Return list of all primary keys.'''
                values = set(super().value_from_datadict(data, files, name))
                # This may only work for MyModel, if MyModel has title field.
                # You need to implement this method yourself, to ensure proper object creation.
                pks = self.queryset.filter(**{'pk__in': list(values)}).values_list('pk', flat=True)
                pks = set(map(str, pks))
                cleaned_values = list(pks)
                for val in values - pks:
                    cleaned_values.append(self.queryset.create(title=val).pk)
                return cleaned_values

    """
