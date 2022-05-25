from django.http import HttpResponse, HttpRequest, FileResponse, Http404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.conf import settings

from .models import Category, EduMaterial


class PdfFileView(View):
    def get(self, request: HttpRequest, ) -> FileResponse:
        file_path = settings.BASE_DIR / "catalog/pdfmaterials/sample_pdf.pdf"

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
