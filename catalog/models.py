from django.db import models
from django.shortcuts import reverse


class EduMaterial(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(max_length=1000)
    author = models.ForeignKey('Author', null=True, on_delete=models.SET_NULL)

    ACCESS_TYPE = (
        ('e', 'Everybody can access'),
        ('s', 'Sign up to access'),
        ('p', 'For premium users'),
    )
    access_type = models.CharField(max_length=1, choices=ACCESS_TYPE, default='e')
    pdf_file = models.FileField(upload_to="pdfmaterials/")
    category = models.ManyToManyField('Category')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('edumaterial-detail', args=[str(self.id)])

    def get_absolute_file_url(self):
        return reverse('edumaterial-file', args=[str(self.id)])


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    info = models.TextField(max_length=1000)

    class Meta:
        ordering = ["-last_name"]

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])


class Category(models.Model):
    name = models.CharField(max_length=100)
    info = models.TextField(max_length=1000)
    parent_category = models.ForeignKey('Category',
                                        null=True, blank=True,
                                        on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.id)])
