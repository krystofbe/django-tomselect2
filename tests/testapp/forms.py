from django import forms
from django.utils.encoding import force_str

from django_tomselect2.forms import (
    HeavyTomSelectMultipleWidget,
    HeavyTomSelectWidget,
    ModelTomSelectMultipleWidget,
    ModelTomSelectTagWidget,
    ModelTomSelectWidget,
    TomSelectMultipleWidget,
    TomSelectWidget,
)
from tests.testapp import models
from tests.testapp.models import Album, Artist, City, Country, Genre


class TitleSearchFieldMixin:
    search_fields = ["title__icontains", "pk__startswith"]


class TitleModelTomSelectWidget(TitleSearchFieldMixin, ModelTomSelectWidget):
    pass


class TitleModelTomSelectMultipleWidget(
    TitleSearchFieldMixin, ModelTomSelectMultipleWidget
):
    pass


class GenreTomSelectTagWidget(TitleSearchFieldMixin, ModelTomSelectTagWidget):
    model = models.Genre

    def create_value(self, value):
        self.get_queryset().create(title=value)


class ArtistCustomTitleWidget(ModelTomSelectWidget):
    model = Artist
    search_fields = ["title__icontains"]

    def label_from_instance(self, obj):
        return force_str(obj.title).upper()


class GenreCustomTitleWidget(ModelTomSelectWidget):
    model = Genre
    search_fields = ["title__icontains"]

    def label_from_instance(self, obj):
        return force_str(obj.title).upper()


class ArtistDataViewWidget(HeavyTomSelectWidget):
    data_view = "heavy_data_1"


class PrimaryGenreDataUrlWidget(HeavyTomSelectWidget):
    data_url = "/heavy_data_2/"


class AlbumTomSelectWidgetForm(forms.ModelForm):
    class Meta:
        model = models.Album
        fields = (
            "artist",
            "primary_genre",
        )
        widgets = {
            "artist": TomSelectWidget,
            "primary_genre": TomSelectWidget,
        }


class AlbumTomSelectMultipleWidgetForm(forms.ModelForm):
    class Meta:
        model = models.Album
        fields = (
            "genres",
            "featured_artists",
        )
        widgets = {
            "genres": TomSelectMultipleWidget,
            "featured_artists": TomSelectMultipleWidget,
        }


class AlbumModelTomSelectWidgetForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = (
            "artist",
            "primary_genre",
        )
        widgets = {
            "artist": ArtistCustomTitleWidget(),
            "primary_genre": GenreCustomTitleWidget(
                dependent_fields={"artist": "artist"}
            ),
        }


class AlbumModelTomSelectMultipleWidgetRequiredForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = (
            "genres",
            "featured_artists",
        )
        widgets = {
            "genres": TitleModelTomSelectMultipleWidget,
            "featured_artists": TitleModelTomSelectMultipleWidget,
        }


class ArtistModelTomSelectMultipleWidgetForm(forms.Form):
    title = forms.CharField(max_length=50)
    genres = forms.ModelMultipleChoiceField(
        widget=ModelTomSelectMultipleWidget(
            queryset=models.Genre.objects.all(),
            search_fields=["title__icontains"],
        ),
        queryset=models.Genre.objects.all(),
        required=True,
    )

    featured_artists = forms.ModelMultipleChoiceField(
        widget=ModelTomSelectMultipleWidget(
            queryset=models.Artist.objects.all(),
            search_fields=["title__icontains"],
        ),
        queryset=models.Artist.objects.all(),
        required=False,
    )


NUMBER_CHOICES = [
    (1, "One"),
    (2, "Two"),
    (3, "Three"),
    (4, "Four"),
]


class TomSelectClearableWidget(TomSelectWidget):
    plugins = {"clear_button": {}}


class TomSelectClearableMultipleWidget(TomSelectMultipleWidget):
    plugins = {"clear_button": {}}


class TomSelectWidgetForm(forms.Form):
    number = forms.ChoiceField(
        widget=TomSelectClearableWidget, choices=NUMBER_CHOICES, required=False
    )


class TomSelectMultipleWidgetForm(forms.Form):
    numbers = forms.MultipleChoiceField(
        widget=TomSelectClearableMultipleWidget,
        choices=NUMBER_CHOICES,
        required=False,
    )


class HeavyTomSelectWidgetForm(forms.Form):
    artist = forms.ChoiceField(widget=ArtistDataViewWidget(), choices=NUMBER_CHOICES)
    primary_genre = forms.ChoiceField(
        widget=PrimaryGenreDataUrlWidget(),
        required=False,
        choices=NUMBER_CHOICES,
    )


class HeavyTomSelectMultipleWidgetForm(forms.Form):
    title = forms.CharField(max_length=50)
    genres = forms.MultipleChoiceField(
        widget=HeavyTomSelectMultipleWidget(
            data_view="heavy_data_1",
            choices=NUMBER_CHOICES,
            attrs={"data-minimum-input-length": 0},
        ),
        choices=NUMBER_CHOICES,
    )
    featured_artists = forms.MultipleChoiceField(
        widget=HeavyTomSelectMultipleWidget(
            data_view="heavy_data_2",
            choices=NUMBER_CHOICES,
            attrs={"data-minimum-input-length": 0},
        ),
        choices=NUMBER_CHOICES,
        required=False,
    )

    def clean_title(self):
        if len(self.cleaned_data["title"]) < 3:
            raise forms.ValidationError("Title must have more than 3 characters.")
        return self.cleaned_data["title"]


class ModelTomSelectTagWidgetForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["genres"]
        widgets = {"genres": GenreTomSelectTagWidget}


class AddressChainedTomSelectWidgetForm(forms.Form):
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label="Country",
        widget=ModelTomSelectWidget(
            search_fields=["name__icontains"],
            max_results=500,
            dependent_fields={"city": "cities"},
            attrs={"data-minimum-input-length": 0},
        ),
    )

    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        label="City",
        widget=ModelTomSelectWidget(
            search_fields=["name__icontains"],
            dependent_fields={"country": "country"},
            max_results=500,
            attrs={"data-minimum-input-length": 0},
        ),
    )

    city2 = forms.ModelChoiceField(
        queryset=City.objects.all(),
        label="City not Interdependent",
        widget=ModelTomSelectWidget(
            search_fields=["name__icontains"],
            dependent_fields={"country": "country"},
            max_results=500,
            attrs={"data-minimum-input-length": 0},
        ),
    )


class GroupieForm(forms.ModelForm):
    class Meta:
        model = models.Groupie
        fields = ["id", "obsession"]
        widgets = {"obsession": ArtistCustomTitleWidget}


class CityModelTomSelectWidget(ModelTomSelectWidget):
    model = City
    search_fields = ["name"]

    def result_from_instance(self, obj, request):
        return {"id": obj.pk, "text": obj.name, "country": str(obj.country)}


class CityForm(forms.Form):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(), widget=CityModelTomSelectWidget(), required=False
    )
