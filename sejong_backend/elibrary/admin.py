from django.contrib import admin
from django.utils.html import format_html
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # cover_id и file_id заполняются автоматически — только для чтения
    readonly_fields = ('cover_id', 'file_id', 'cover_preview')

    list_display = ('title_eng', 'author', 'genres', 'published_date', 'created_at', 'cover_preview')
    list_filter = ('genres', 'published_date', 'created_at')
    search_fields = ('title_eng', 'title_rus', 'author')

    fieldsets = (
        ('Названия', {
            'fields': ('title_eng', 'title_rus', 'title_taj', 'title_kor')
        }),
        ('Описания', {
            'fields': ('description_eng', 'description_rus', 'description_taj', 'description_kor'),
            'classes': ('collapse',),
        }),
        ('Детали', {
            'fields': ('author', 'genres', 'published_date')
        }),
        ('Файлы', {
            'fields': ('cover', 'cover_preview', 'cover_id', 'file', 'file_id')
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_id:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />',
                obj.cover_id
            )
        return '—'
    cover_preview.short_description = 'Превью'
