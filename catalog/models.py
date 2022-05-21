from django.db import models
from django.urls import reverse
from uuid import uuid4


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
    language = models.ForeignKey(Language, on_delete=models.RESTRICT)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, help_text="Unique ID for this book in this library")
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

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

    def __str__(self):
        return f"{self.id} - {self.book.title}"


class Author(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return self.last_name + ", " + self.first_name
