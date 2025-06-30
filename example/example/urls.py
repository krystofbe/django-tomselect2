from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.Bootstrap5BookCreateView.as_view(), name="book-create"),
    path(
        "category-autocomplete/",
        views.CategoryAutocomplete.as_view(),
        name="category_autocomplete",
    ),
    path(
        "tags-autocomplete/", views.TagsAutocomplete.as_view(), name="tags_autocomplete"
    ),
    path(
        "keywords-autocomplete/",
        views.KeywordsAutocomplete.as_view(),
        name="keywords_autocomplete",
    ),
    path(
        "author-specialization-autocomplete/",
        views.AuthorSpecializationAutoCompleteView.as_view(),
        name="author_specialization_autocomplete",
    ),
    path(
        "book-autocomplete/",
        views.BookAutocomplete.as_view(),
        name="book_autocomplete",
    ),
    path("tomselect2/", include("django_tomselect2.urls")),
    path("admin/", admin.site.urls),
]
