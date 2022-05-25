from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("categories/", views.CategoriesView.as_view(), name="category-list"),
]
