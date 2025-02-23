from django.views import generic

from django_tomselect2.views import AutoResponseView

from . import forms, models


class CategoryAutocomplete(AutoResponseView):
    def get_queryset(self):
        return models.Category.objects.all()


class TagsAutocomplete(AutoResponseView):
    def get_queryset(self):
        return models.Tag.objects.all()


class KeywordsAutocomplete(AutoResponseView):
    def get_queryset(self):
        return models.Tag.objects.all()


class AuthorSpecializationAutoCompleteView(AutoResponseView):
    def get_queryset(self):
        author_id = self.request.GET.get("author", None)
        qs = models.AuthorSpecialization.objects.all()
        if author_id:
            qs = qs.filter(author_id=author_id)
        return qs


class BookAutocomplete(AutoResponseView):
    def get_queryset(self):
        author_id = self.request.GET.get("author")
        specialization_id = self.request.GET.get("specialization")
        qs = models.Book.objects.all()
        if author_id:
            qs = qs.filter(author_id=author_id)
        if specialization_id:
            qs = qs.filter(author__specializations__id=specialization_id)
        return qs


class Bootstrap5BookCreateView(generic.CreateView):
    model = models.Book
    form_class = forms.BookForm
    success_url = "/"
    template_name = "example/bootstrap5/book_form.html"
