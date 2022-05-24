from django.db import models
from django.shortcuts import reverse


class EduMaterial(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    summary = models.TextField(max_length=1000, verbose_name="Описание")
    author = models.ForeignKey('Author', verbose_name="Автор", null=True, on_delete=models.SET_NULL)

    ACCESS_TYPE = (
        ('e', 'Доступен всем'),
        ('s', 'Доступен только зарегистрированным'),
        ('p', 'Только для премиум'),
    )
    access_type = models.CharField(max_length=1, choices=ACCESS_TYPE, default='e', verbose_name="Доступ")
    pdf_file = models.FileField(verbose_name="Файл", upload_to="pdfmaterials/")
    subcategory = models.ManyToManyField('Subcategory', verbose_name="Подкатегория")

    def get_absolute_url(self):
        return reverse('edumaterial-detail', args=[str(self.id)])


class Author(models.Model):
    first_name = models.CharField(verbose_name="Имя", max_length=100)
    last_name = models.CharField(verbose_name="Фамилия", max_length=100)
    info = models.TextField(verbose_name="Информация", max_length=1000)

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])


class Category(models.Model):
    name = models.CharField(verbose_name="Название категории", max_length=100)
    info = models.TextField(verbose_name="Описание категории", max_length=1000)
    parent_category = models.ForeignKey('Category',
                                        null=True,
                                        verbose_name="Принадлежит к категории",
                                        on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.id)])
