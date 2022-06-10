import threading

from django.http import HttpResponse, HttpRequest, FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django import forms
from django.core.mail import send_mass_mail
from django.views import View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)
from django.views.generic.edit import CreateView, FormView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import Category, EduMaterial, Author
from .forms import UserRegisterForm, GetUserCardDataForm


def send_notify_about_category(category: Category):
    users = [user.email for user in category.users_subscribed.all()]

    if len(users) == 0:
        return

    subject = "Category '" + category.name + "' was updated"
    msg = "The category was updated! Don't forget to check it out!"
    message = (subject, msg, 'educatalogteam@example.com', users)
    send_mass_mail((message,), fail_silently=False)


def notify_users_about_category_update(category_name: str):
    print(category_name)
    print("updated")

    category = Category.objects.get(name__exact=category_name)

    threads = [threading.Thread(target=send_notify_about_category, args=(category,))]

    while category.parent_category is not None:
        category = category.parent_category
        threads.append(threading.Thread(target=send_notify_about_category, args=(category,)))

    for t in threads:
        t.start()


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
            if not request.user.has_perm("catalog.can_view_premium"):
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


class SubscribeCategoryView(LoginRequiredMixin, TemplateView):
    template_name = "catalog/subscribe_category.html"
    login_url = reverse_lazy('login')

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        pk = kwargs['pk']
        category = get_object_or_404(Category, pk=pk)
        category.users_subscribed.add(request.user)
        category.save()

        return super(SubscribeCategoryView, self).get(request, *args, **kwargs)


class EduMaterialDetailView(DetailView):
    model = EduMaterial


class EduMaterialEditView(UpdateView):
    model = EduMaterial
    fields = ["title", "summary", "access_type", "pdf_file", "category"]


class EduMaterialDeleteView(DeleteView):
    model = EduMaterial
    success_url = reverse_lazy('category-list')


class EduMaterialCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "catalog.add_edumaterial"
    permission_denied_message = "You cannot add materials!"
    login_url = reverse_lazy("login")
    model = EduMaterial
    fields = ['title', 'summary', 'access_type', 'pdf_file', 'category', 'author']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_form(self, *args, **kwargs):
        form = super(EduMaterialCreateView, self).get_form(*args, **kwargs)
        form.fields['category'].queryset = Category.objects.filter(category__isnull=True)

        EduMaterialCreateView.initial = {'author': self.request.user.author}

        return form

    def form_valid(self, form: forms.Form) -> HttpResponse:
        responce = super().form_valid(form)
        categories_to_update = []

        for category in form.cleaned_data['category']:
            while category is not None:
                if category not in categories_to_update:
                    categories_to_update.append(category)

                category = category.parent_category

        for category in categories_to_update:
            thread = threading.Thread(target=send_notify_about_category, args=(category,))
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
