from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Book, BookInstance, Author, Genre


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
