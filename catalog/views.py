import asyncio

from django.http import HttpResponse, HttpRequest, FileResponse, Http404
from django.core.exceptions import PermissionDenied

from django.views import View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, FormView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import Category, EduMaterial, Author
from .forms import UserRegisterForm, GetUserCardDataForm


async def notify_user(user_num):
    print("send email to user", user_num)
    await asyncio.sleep(user_num)
    print("sent email to user", user_num, "successfully")


async def notify_users_about_category_update(category_name: str):
    print("notify users that the", category_name, "category was updated")

    tasks = []

    for i in range(10):
        tasks.append(notify_user(i))

    await asyncio.gather(*tasks)
    print("finished notifying")


async def async_view(request: HttpRequest) -> HttpResponse:
    loop = asyncio.get_event_loop()
    loop.create_task(notify_users_about_category_update("math"))
    return HttpResponse("Yes, I am async!")


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
                           EduMaterial.objects.filter(summary__icontains=usr_query) | \
                           EduMaterial.objects.filter(author__first_name__icontains=usr_query) | \
                           EduMaterial.objects.filter(author__last_name__icontains=usr_query)
        return filtered_objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
