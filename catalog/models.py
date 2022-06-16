"""Models for catalog app."""

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse


class EduMaterial(models.Model):
    """Educational material model. Has an Author and is located inside of a Category."""

    title = models.CharField(max_length=200, db_index=True)
    summary = models.TextField(max_length=1000, db_index=True)
    author = models.ForeignKey('Author', null=True, on_delete=models.SET_NULL)

    ACCESS_TYPE = (
        ('e', 'Everybody can access'),
        ('s', 'Sign up to access'),
        ('p', 'For premium users'),
    )
    access_type = models.CharField(max_length=1, choices=ACCESS_TYPE, default='e')
    pdf_file = models.FileField(upload_to="pdfmaterials/")
    category = models.ManyToManyField('Category')

    class Meta:
        """Meta info."""

        permissions = (("can_view_premium", "View premium materials"),)

    def __str__(self) -> str:
        """Convert material to string."""
        return str(self.title)

    def get_absolute_url(self) -> str:
        """Get the absolute url for the material."""
        return reverse('edumaterial-detail', args=[str(self.id)])

    def get_absolute_file_url(self) -> str:
        """Get the url to access the file."""
        return reverse('edumaterial-file', args=[str(self.id)])


class Author(models.Model):
    """The author of the material. Has a one-to-one relationship to User."""

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    info = models.TextField(max_length=1000)

    class Meta:
        """Meta info."""

        ordering = ["-last_name"]

    def __str__(self) -> str:
        """Convert author to string."""
        return self.first_name + " " + self.last_name

    def get_absolute_url(self) -> str:
        """Get the absolute url of the author."""
        return reverse('author-detail', args=[str(self.id)])


class Category(models.Model):
    """Category of educational materials. Can itself be inside other category."""

    name = models.CharField(max_length=100, db_index=True)
    info = models.TextField(max_length=1000)
    parent_category = models.ForeignKey('Category',
                                        null=True, blank=True,
                                        on_delete=models.CASCADE)
    users_subscribed = models.ManyToManyField(User, blank=True)

    def __str__(self) -> str:
        """Convert model instance to string."""
        return str(self.name)

    def get_absolute_url_for_subscribe(self) -> str:
        """Get the absolute url of the category, which can be used to subscribe."""
        return reverse('category-subscribe', args=[str(self.id)])

    def get_absolute_url(self) -> str:
        """Get the absolute url of the category."""
        return reverse('category-detail', args=[str(self.id)])
