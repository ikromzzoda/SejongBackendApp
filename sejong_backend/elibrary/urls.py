from django.urls import path
from .views import BookListView, BookDetailView

urlpatterns = [
    path('elibrary/', BookDetailView.as_view(), name='book-list'),
    path('elibrary/<pk>/', BookDetailView.as_view(), name='book-detail'),
]
