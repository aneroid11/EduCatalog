from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from uuid import uuid4
from datetime import date


class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="For example, Science Fiction or Horror")

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=200, help_text="The language in which the book is written")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Brief description")
    isbn = models.CharField("ISBN", max_length=13, unique=True,
                            help_text="13 Character "
                                      "<a href='https://www.isbn-international.org/content/what-isbn'>"
                                      "ISBN number"
                                      "</a>")
    genre = models.ManyToManyField(Genre, help_text="Select a genre to the book")
    language = models.ForeignKey(Language, on_delete=models.RESTRICT, null=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        return ", ".join(genre.name for genre in self.genre.all())

    display_genre.short_description = "Genre"


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, help_text="Unique ID for this book in this library")
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved")
    )

    status = models.CharField(max_length=1,
                              choices=LOAN_STATUS,
                              blank=True,
                              default="m",
                              help_text="Book availability")

    class Meta:
        ordering = ["due_back"]

        permissions = (("can_mark_returned", "Отметить, что книга возвращена"),)

    def __str__(self):
        return f"{self.id} - {self.book.title}"

    @property
    def is_overdue(self):
        return self.due_back and self.due_back < date.today()


class Author(models.Model):
    first_name = models.CharField(max_length=200, verbose_name="Имя")
    last_name = models.CharField(max_length=200, verbose_name="Фамилия")

    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    date_of_death = models.DateField(null=True, blank=True, verbose_name="Дата смерти")

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return self.last_name + ", " + self.first_name
