import threading

from django.http import HttpResponse, HttpRequest, FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django import forms
from django.core.mail import send_mass_mail
from django.views import View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, FormView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import Category, EduMaterial, Author
from .forms import UserRegisterForm, GetUserCardDataForm


def notify_users_about_category_update(category_name: str):
    print("notify users about category update:", category_name)
    print("finished notifying")


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')
    form_class = UserRegisterForm
    success_message = "Your account was created successfully!"


class MaterialFileView(View):
    def get(self, request: HttpRequest, pk: int) -> FileResponse:
        material = get_object_or_404(EduMaterial, pk=pk)

        if material.access_type == "s":
            if not request.user.is_authenticated:
                raise PermissionDenied
        elif material.access_type == "p":
            if (not request.user.is_authenticated or not request.user.has_perm("catalog.can_view_premium")) \
                    and request.user.author is None:
                raise PermissionDenied

        file_path = settings.BASE_DIR / material.pdf_file.path

        try:
            return FileResponse(open(file_path, "rb"), content_type="application/pdf")
        except FileNotFoundError:
            raise Http404()


class IndexView(TemplateView):
    template_name = "catalog/index.html"


class CategoriesView(ListView):
    model = Category


class CategoryDetailView(DetailView):
    model = Category


class SubscribeCategoryView(TemplateView, LoginRequiredMixin):
    template_name = "catalog/subscribe_category.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        pk = kwargs['pk']
        category = get_object_or_404(Category, pk=pk)
        category.users_subscribed.add(request.user)
        category.save()

        return super(SubscribeCategoryView, self).get(*args, **kwargs)


class EduMaterialDetailView(DetailView):
    model = EduMaterial


class EduMaterialCreateView(CreateView):
    model = EduMaterial
    fields = ['title', 'summary', 'access_type', 'pdf_file', 'category', 'author']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category_to_update = None

    def get_form(self, *args, **kwargs):
        form = super(EduMaterialCreateView, self).get_form(*args, **kwargs)
        form.fields['category'].queryset = Category.objects.filter(category__isnull=True)
        self.category_to_update = str(form.fields['category'])

        EduMaterialCreateView.initial = {'author': self.request.user.author}

        return form

    def form_valid(self, form: forms.Form) -> HttpResponse:
        responce = super().form_valid(form)

        category_name = self.category_to_update
        thread = threading.Thread(target=notify_users_about_category_update, args=(category_name,))
        thread.start()

        return responce


class AuthorListView(ListView):
    model = Author


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
                           EduMaterial.objects.filter(summary__icontains=usr_query) | \
                           EduMaterial.objects.filter(author__first_name__icontains=usr_query) | \
                           EduMaterial.objects.filter(author__last_name__icontains=usr_query)
        return filtered_objects


class GetPremiumView(FormView):
    template_name = "catalog/get_premium_card_data.html"
    form_class = GetUserCardDataForm
    success_url = reverse_lazy('get-premium-thanks')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        content_type = ContentType.objects.get_for_model(EduMaterial)
        permission = Permission.objects.get(codename="can_view_premium", content_type=content_type)
        self.request.user.user_permissions.add(permission)

        return super().form_valid(form)


class GetPremiumThanksView(TemplateView):
    template_name = "catalog/get_premium_thanks.html"
