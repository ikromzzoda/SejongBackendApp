from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Book
from .serializers import BookSerializer


class BookListView(ListAPIView):
    """
    GET /api/elibrary/
    Возвращает список всех книг.
    Поддерживает фильтрацию по жанру и поиск по названию/автору.

    Примеры:
        /api/elibrary/?genres=Книги Sejong
        /api/elibrary/?search=корейский
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Фильтрация и поиск — django-filter уже стоит в requirements.txt
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genres']
    search_fields = ['title_eng', 'title_rus', 'title_taj', 'title_kor', 'author']
    ordering_fields = ['created_at', 'published_date']
    ordering = ['-created_at']


class BookDetailView(RetrieveAPIView):
    """
    GET /api/elibrary/<id>/
    Возвращает одну книгу по ID.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
