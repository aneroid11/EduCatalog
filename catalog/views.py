from django.http import HttpResponse, HttpRequest, FileResponse, Http404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import Category, EduMaterial, Author


class MaterialFileView(View):
    def get(self, request: HttpRequest, pk: int) -> FileResponse:
        material = get_object_or_404(EduMaterial, pk=pk)

        # file_path = settings.BASE_DIR / "catalog/pdfmaterials/sample_pdf.pdf"
        file_path = settings.BASE_DIR / material.pdf_file.path

        try:
            return FileResponse(open(file_path, "rb"), content_type="application/pdf")
        except FileNotFoundError:
            raise Http404()


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


class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class EduMaterialDetailView(DetailView):
    model = EduMaterial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AuthorListView(ListView):
    model = Author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AuthorDetailView(DetailView):
    model = Author


class SearchView(ListView):
    model = EduMaterial
    template_name = "catalog/search.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        usr_query = self.request.GET['usr_query']
        filtered_objects = EduMaterial.objects.filter(title__icontains=usr_query) | \
                           EduMaterial.objects.filter(summary__icontains=usr_query)
        return filtered_objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
