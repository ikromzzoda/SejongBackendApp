from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    readonly_fields = ('cover_id', 'file_id',)

    list_display = ("title_eng", "author", "published_date", "created_at")
    search_fields = ("title_eng", "author")
    list_filter = ("published_date", "created_at")
