from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import EduMaterial, Author, Category


class AuthorInline(admin.StackedInline):
    model = Author
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (AuthorInline,)


admin.site.register(EduMaterial)
admin.site.register(Author)
admin.site.register(Category)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
