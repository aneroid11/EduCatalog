from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("categories/", views.CategoriesView.as_view(), name="category-list"),
    path("category/<int:pk>", views.CategoryDetailView.as_view(), name="category-detail"),
    path("material/<int:pk>", views.EduMaterialDetailView.as_view(), name="edumaterial-detail"),
]
