import datetime
import uuid
import logging

from django.conf import settings
from django.shortcuts import render, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

from .models import Book, BookInstance, Author, Genre
from .forms import RenewBookForm


def index(request: HttpRequest) -> HttpResponse:
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    num_books_with_jojo = Book.objects.filter(title__icontains="jojo").count()

    num_user_visits = request.session.get("num_user_visits", 0)
    num_user_visits += 1
    request.session["num_user_visits"] = num_user_visits

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genres": num_genres,
        "num_books_with_jojo": num_books_with_jojo,
        "num_user_visits": num_user_visits,
    }

    return render(request, "catalog/index.html", context)


def sample_pdf_view(request: HttpRequest):
    file_path = settings.BASE_DIR / "catalog/pdfmaterials/sample_pdf.pdf"

    try:
        return FileResponse(open(file_path, "rb"), content_type="application/pdf")
    except FileNotFoundError:
        raise Http404()


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
    bookinstance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            bookinstance.due_back = form.cleaned_data['due_back']
            bookinstance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        # default form.
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"due_back": proposed_renewal_date})

    context = {
        "form": form,
        "bookinstance": bookinstance,
    }

    return render(request, "catalog/book_renew_librarian.html", context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by("due_back")


class AllLoanedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_all_borrowed.html'
    paginate_by = 10
    permission_required = ('catalog.can_mark_returned',)

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by("due_back")


class AuthorCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('catalog.can_mark_returned',)
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '2222-01-01'}


class AuthorUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.can_mark_returned',)
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ("catalog.can_mark_returned",)
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('catalog.can_mark_returned',)
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    initial = {"title": "Новая книга"}


class BookUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.can_mark_returned',)
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]


class BookDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ("catalog.can_mark_returned",)
    model = Book
    success_url = reverse_lazy('books')
