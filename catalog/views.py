"""Views for the app."""

import threading
import logging

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
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import Category, EduMaterial, Author
from .forms import UserRegisterForm, GetUserCardDataForm

from django.core.files.storage import default_storage as storage

logging.basicConfig(filename="logs.txt", level=logging.INFO)
logger = logging.getLogger(__name__)


def send_notify_about_category(category_id: int):
    """Send an email to all users subscribed to the category."""
    try:
        category = Category.objects.get(id=category_id)
    except Exception as e:
        logger.warning("cannot send notify about category")
        logger.warning(str(e))
        return

    logger.info("Send notifications about the update of " + category.name + " category")

    users = [user.email for user in category.users_subscribed.all()]

    if len(users) == 0:
        logger.warning("No users to send notifications about the update of " + category.name + " category")
        return

    subject = "Category '" + category.name + "' was updated"
    msg = "The category was updated! Don't forget to check it out!"
    message = (subject, msg, 'educatalogteam@example.com', users)
    send_mass_mail((message,), fail_silently=False)
    logger.warning("Notifications sent successfully")


class SignUpView(SuccessMessageMixin, CreateView):
    """The view to sign up a user."""

    template_name = "registration/register.html"
    success_url = reverse_lazy('login')
    form_class = UserRegisterForm
    success_message = "Your account was created successfully!"


class MaterialFileView(View):
    """The view to access the actual pdf file."""

    def get(self, request: HttpRequest, pk: int) -> FileResponse:
        """Check if the user has permissions to access the file."""
        logger.info("request for file: " + str(pk))
        logger.info("getting the material")
        material = get_object_or_404(EduMaterial, pk=pk)

        if material.access_type == "s":
            if not request.user.is_authenticated:
                logger.error("user is not authenticated and the material access type is signed up only!")
                raise PermissionDenied
        elif material.access_type == "p":
            if not request.user.has_perm("catalog.can_view_premium"):
                logger.error("user cannot view premium materials but requests a premium material download!")
                raise PermissionDenied

        fh = storage.open(material.pdf_file.name, "rb")

        try:
            return FileResponse(fh, content_type="application/pdf")
        except FileNotFoundError:
            logger.error("there is no such file on the server")
            raise Http404()


class IndexView(TemplateView):
    """Main page."""

    template_name = "catalog/index.html"


class CategoriesView(ListView):
    """List of main categories."""

    model = Category


class CategoryDetailView(DetailView):
    """View that shows the category and all nested categories."""

    model = Category


class SubscribeCategoryView(LoginRequiredMixin, TemplateView):
    """The view to subscribe to a category."""

    template_name = "catalog/subscribe_category.html"
    login_url = reverse_lazy('login')

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Subscribe user to a category."""
        pk = kwargs['pk']
        category = get_object_or_404(Category, pk=pk)
        category.users_subscribed.add(request.user)
        category.save()
        logger.info("subscribe to category with index: " + str(pk))

        return super(SubscribeCategoryView, self).get(request, *args, **kwargs)


class EduMaterialDetailView(DetailView):
    """Information about a educational material."""

    model = EduMaterial


class EduMaterialEditView(UpdateView):
    """View to edit a material."""

    model = EduMaterial
    fields = ["title", "summary", "access_type", "pdf_file", "category"]


class EduMaterialDeleteView(DeleteView):
    """View to delete a material."""

    model = EduMaterial
    success_url = reverse_lazy('category-list')


class EduMaterialCreateView(PermissionRequiredMixin, CreateView):
    """View to create a material."""

    permission_required = "catalog.add_edumaterial"
    permission_denied_message = "You cannot add materials!"
    login_url = reverse_lazy("login")
    model = EduMaterial
    fields = ['title', 'summary', 'access_type', 'pdf_file', 'category', 'author']

    def get_form(self, *args, **kwargs):
        """Alter category and author fields."""
        form = super(EduMaterialCreateView, self).get_form(*args, **kwargs)
        form.fields['category'].queryset = Category.objects.filter(category__isnull=True)

        EduMaterialCreateView.initial = {'author': self.request.user.author}

        return form

    def form_valid(self, form: forms.Form) -> HttpResponse:
        """Start threads that notify users."""
        responce = super().form_valid(form)
        categories_to_update = []

        for category in form.cleaned_data['category']:
            while category is not None:
                if category not in categories_to_update:
                    categories_to_update.append(category)

                category = category.parent_category

        logger.info("starting threads that send messages about the category update")
        for category in categories_to_update:
            print(category)
            print(category.users_subscribed.all())

            # send_notify_about_category(category_id=category.id)
            thread = threading.Thread(target=send_notify_about_category, args=(category.id,))
            thread.start()

        return responce


class AuthorListView(ListView):
    """List of authors."""

    model = Author


class AuthorDetailView(DetailView):
    """Author page."""

    model = Author


class SearchView(ListView):
    """View for searching for a particular material."""

    model = EduMaterial
    template_name = "catalog/search.html"

    def get_queryset(self):
        """Get the materials that contain the query."""
        usr_query = self.request.GET['usr_query']
        logger.info("user searched: " + usr_query)
        filtered_objects = EduMaterial.objects.filter(title__icontains=usr_query) | \
                           EduMaterial.objects.filter(summary__icontains=usr_query) | \
                           EduMaterial.objects.filter(author__first_name__icontains=usr_query) | \
                           EduMaterial.objects.filter(author__last_name__icontains=usr_query)
        return filtered_objects


class GetPremiumView(FormView):
    """View for getting card data from the user."""

    template_name = "catalog/get_premium_card_data.html"
    form_class = GetUserCardDataForm
    success_url = reverse_lazy('get-premium-thanks')

    def form_valid(self, form):
        """Grant permission to view premium."""
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        content_type = ContentType.objects.get_for_model(EduMaterial)
        permission = Permission.objects.get(codename="can_view_premium", content_type=content_type)
        self.request.user.user_permissions.add(permission)

        logger.info("added premium to user: " + str(self.request.user))

        return super().form_valid(form)


class GetPremiumThanksView(TemplateView):
    """Premium 'thanks' view."""

    template_name = "catalog/get_premium_thanks.html"
