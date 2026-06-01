from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """
    Сериализатор книги.
    Вложенные объекты title/description формируются из плоских полей модели,
    чтобы фронтенд получал удобную структуру без изменения схемы БД.
    """

    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'description',
            'author',
            'cover',   # cover_id — прямая ссылка на обложку
            'file',    # file_id  — прямая ссылка для скачивания
            'genres',
            'published_date',
            'created_at',
        ]

    def get_title(self, obj):
        return {
            'taj': obj.title_taj,
            'rus': obj.title_rus,
            'eng': obj.title_eng,
            'kor': obj.title_kor,
        }

    def get_description(self, obj):
        return {
            'taj': obj.description_taj,
            'rus': obj.description_rus,
            'eng': obj.description_eng,
            'kor': obj.description_kor,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Подменяем cover/file на кешированные прямые ссылки
        data['cover'] = instance.cover_id
        data['file']  = instance.file_id
        return data
