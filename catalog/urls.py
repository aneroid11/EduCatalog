from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("categories", views.CategoriesView.as_view(), name="category-list"),
    path("category/<int:pk>", views.CategoryDetailView.as_view(), name="category-detail"),
    path("material/<int:pk>", views.EduMaterialDetailView.as_view(), name="edumaterial-detail"),
    path("material/<int:pk>/file", views.MaterialFileView.as_view(), name="edumaterial-file"),
    path("authors", views.AuthorListView.as_view(), name='author-list'),
    path("author/<int:pk>", views.AuthorDetailView.as_view(), name='author-detail'),
]
