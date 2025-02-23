from django import forms

from django_tomselect2 import forms as ts2forms

from . import models


class AllPluginsTomSelectWidget(ts2forms.ModelTomSelectWidget):
    plugins = {
        "caret_position": {},
        "drag_drop": {},
        "clear_button": {
            "title": "Remove all selected options",
            "htmlTemplate": '<div class="${data.className}" title="${data.title}">&times;</div>',
        },
        "dropdown_header": {
            "title": "Select an Option",
            "htmlTemplate": """
                <div class="${data.headerClass}">
                    <div class="${data.titleRowClass}">
                        <span class="${data.labelClass}">${data.title}</span>
                        <a class="${data.closeClass}">&times;</a>
                    </div>
                </div>
            """,
        },
        "dropdown_input": {},
        "no_active_items": {},
        "no_backspace_delete": {},
        "optgroup_columns": {},
    }


class AuthorModelWidget(AllPluginsTomSelectWidget):
    search_fields = ["username__istartswith", "email__icontains"]
    theme = "bootstrap5"
    dependent_fields = {"specialization": "author__specializations"}


class AuthorSpecializationWidget(ts2forms.ModelTomSelectWidget):
    search_fields = ["name__istartswith"]
    theme = "bootstrap5"
    dependent_fields = {"author": "author"}
    data_view = "author_specialization_autocomplete"


class HeavyCategoryWidget(ts2forms.ModelTomSelectMixin, ts2forms.HeavyTomSelectWidget):
    data_view = "category_autocomplete"
    theme = "bootstrap5"


class BookReviewWidget(ts2forms.ModelTomSelectWidget):
    search_fields = ["review_text__icontains"]
    theme = "bootstrap5"
    dependent_fields = {"author": "book__author", "books": "book"}
    data_view = "book_review_autocomplete"


class BookForm(forms.ModelForm):
    # Extra (non-model) fields:
    specialization = forms.ModelChoiceField(
        queryset=models.AuthorSpecialization.objects.all(),
        widget=AuthorSpecializationWidget(
            attrs={"placeholder": "Select specialization"},
            tom_select_settings={"preload": True},
        ),
        help_text=(
            "This field uses a dependent autocomplete feature: options are filtered "
            "based on the selected author. It demonstrates how to trigger dynamic changes "
            "in available specializations using django-tomselect2."
        ),
    )
    books = forms.ModelMultipleChoiceField(
        queryset=models.Book.objects.all(),
        widget=ts2forms.ModelTomSelectMultipleWidget(
            data_view="book_autocomplete",
            dependent_fields={"author": "author", "specialization": "specialization"},
            attrs={"placeholder": "Filter related books"},
            theme="bootstrap5",
        ),
        required=False,
        help_text=(
            "This multi-select field demonstrates dynamic AJAX filtering based on dependent "
            "fields (author and specialization). It shows how django-tomselect2 can be used "
            "for advanced, relational filtering in multi-selects."
        ),
    )
    publisher = forms.ChoiceField(
        choices=[
            ("publisher1", "Publisher 1"),
            ("publisher2", "Publisher 2"),
        ],
        widget=ts2forms.TomSelectWidget(
            attrs={"placeholder": "Select publisher"},
            theme="bootstrap5",
        ),
        help_text=(
            "This field uses a basic Tom Select widget with a placeholder. It highlights the standard "
            "dropdown enhancement provided by django-tomselect2."
        ),
    )
    reviews = forms.ModelMultipleChoiceField(
        queryset=models.BookReview.objects.all(),
        widget=BookReviewWidget(
            attrs={"placeholder": "Select reviews"},
            tom_select_settings={"preload": True},
        ),
        required=False,
        help_text=(
            "This field demonstrates a three-level dependency chain: "
            "Author → Book → Reviews. Selecting an author filters available books, "
            "which then filters available reviews."
        ),
    )

    class Meta:
        model = models.Book
        # Only include model fields: “title”, “author”, “publisher”, and “category”
        fields = ["title", "author", "publisher", "category"]
        widgets = {
            "author": AuthorModelWidget(
                attrs={"placeholder": "Select an author"},
                tom_select_settings={"preload": True},
            ),
            "category": HeavyCategoryWidget(
                attrs={"placeholder": "Select a category"},
                search_fields=["name__icontains"],
            ),
        }
        help_texts = {
            "title": "Regular text input for the book's title (no Tom Select enhancements).",
            "author": (
                "This field uses a Tom Select widget with custom plugins (e.g., clear button, dropdown header) "
                "and demonstrates dependency by updating specializations based on the selected author."
            ),
            "publisher": "A standard Tom Select-enhanced dropdown with a placeholder.",
            "category": (
                "This field uses a heavy Tom Select widget that loads options via AJAX, "
                "ideal for large datasets such as a list of categories."
            ),
        }
