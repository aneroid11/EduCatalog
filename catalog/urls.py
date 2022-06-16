"""The catalog app urls."""

from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("categories", views.CategoriesView.as_view(), name="category-list"),
    path("category/<int:pk>", views.CategoryDetailView.as_view(), name="category-detail"),
    path("category/<int:pk>/subscribe", views.SubscribeCategoryView.as_view(), name="category-subscribe"),
    path("material/create", views.EduMaterialCreateView.as_view(), name='edumaterial-create'),
    path("material/<int:pk>/edit", views.EduMaterialEditView.as_view(), name='edumaterial-edit'),
    path("material/<int:pk>/delete", views.EduMaterialDeleteView.as_view(), name='edumaterial-delete'),
    path("material/<int:pk>", views.EduMaterialDetailView.as_view(), name="edumaterial-detail"),
    path("material/<int:pk>/file", views.MaterialFileView.as_view(), name="edumaterial-file"),
    path("authors", views.AuthorListView.as_view(), name='author-list'),
    path("author/<int:pk>", views.AuthorDetailView.as_view(), name='author-detail'),
    path("search-material", views.SearchView.as_view(), name='search-material'),
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('get-premium', views.GetPremiumView.as_view(), name='get-premium'),
    path('get-premium-thanks', views.GetPremiumThanksView.as_view(), name='get-premium-thanks'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
