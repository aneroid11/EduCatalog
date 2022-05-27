from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import EduMaterial, Author, Category, User


admin.site.register(User, UserAdmin)
admin.site.register(EduMaterial)
admin.site.register(Author)
admin.site.register(Category)
