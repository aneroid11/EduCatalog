from django.contrib import admin
from .models import EduMaterial, Author, Category, Subcategory


admin.site.register(EduMaterial)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Subcategory)
