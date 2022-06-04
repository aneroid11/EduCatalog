from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("categories", views.CategoriesView.as_view(), name="category-list"),
    path("category/<int:pk>", views.CategoryDetailView.as_view(), name="category-detail"),
    path("material/<int:pk>", views.EduMaterialDetailView.as_view(), name="edumaterial-detail"),
    path("material/<int:pk>/file", views.MaterialFileView.as_view(), name="edumaterial-file"),
    path("authors", views.AuthorListView.as_view(), name='author-list'),
    path("author/<int:pk>", views.AuthorDetailView.as_view(), name='author-detail'),
    path("search-material", views.SearchView.as_view(), name='search-material'),
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('get-premium', views.GetPremiumView.as_view(), name='get-premium'),
    # path('get-premium-thanks', views.GetPremiumThanksView.as_view(), name='get-premium-thanks'),
    path('something-async', views.async_view, name='something-async'),
]
