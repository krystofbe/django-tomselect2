from django.urls import include, path

from .forms import (
    AddressChainedTomSelectWidgetForm,
    HeavyTomSelectMultipleWidgetForm,
    HeavyTomSelectWidgetForm,
    ModelTomSelectTagWidgetForm,
    TomSelectMultipleWidgetForm,
    TomSelectWidgetForm,
)
from .views import (
    AlbumModelTomSelectWidgetView,
    TemplateFormView,
    heavy_data_1,
    heavy_data_2,
)

urlpatterns = [
    path(
        "select2_widget",
        TemplateFormView.as_view(form_class=TomSelectWidgetForm),
        name="select2_widget",
    ),
    path(
        "select2_multiple_widget",
        TemplateFormView.as_view(form_class=TomSelectMultipleWidgetForm),
        name="select2_multiple_widget",
    ),
    path(
        "heavy_select2_widget",
        TemplateFormView.as_view(form_class=HeavyTomSelectWidgetForm),
        name="heavy_select2_widget",
    ),
    path(
        "heavy_select2_multiple_widget",
        TemplateFormView.as_view(
            form_class=HeavyTomSelectMultipleWidgetForm, success_url="/"
        ),
        name="heavy_select2_multiple_widget",
    ),
    path(
        "model_select2_widget",
        AlbumModelTomSelectWidgetView.as_view(),
        name="model_select2_widget",
    ),
    path(
        "model_select2_tag_widget",
        TemplateFormView.as_view(form_class=ModelTomSelectTagWidgetForm),
        name="model_select2_tag_widget",
    ),
    path(
        "model_chained_select2_widget",
        TemplateFormView.as_view(form_class=AddressChainedTomSelectWidgetForm),
        name="model_chained_select2_widget",
    ),
    path("heavy_data_1", heavy_data_1, name="heavy_data_1"),
    path("heavy_data_2", heavy_data_2, name="heavy_data_2"),
    path("select2/", include("django_tomselect2.urls")),
]
