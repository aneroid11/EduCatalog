# from django.http import HttpResponse, HttpRequest
from django.views.generic import TemplateView, ListView
from .models import Category


class IndexView(TemplateView):
    template_name = "catalog/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # some more operations with context
        return context


class CategoriesView(ListView):
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
