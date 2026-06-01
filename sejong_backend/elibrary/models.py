from django.db import models
from django.utils import timezone
from gdstorage.storage import GoogleDriveStorage
import re

gd_storage = GoogleDriveStorage()


def extract_drive_id(url: str, download: bool = False) -> str | None:
    """
    Извлекает Google Drive file ID из URL и возвращает прямую ссылку.
    download=True  → ссылка для скачивания файла (PDF и др.)
    download=False → ссылка для просмотра/отображения (обложки)
    """
    match = re.search(r'id=([^&]+)', url)
    if not match:
        return None
    file_id = match.group(1)
    if download:
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    return f'https://drive.google.com/uc?id={file_id}'


class Book(models.Model):
    GENRES_CHOICES = [
        ('Книги Sejong', 'Книги Sejong'),
        ('Книги Topik', 'Книги Topik'),
        ('Художественная литература', 'Художественная литература'),
    ]

    # Названия на 4 языках
    title_taj = models.CharField(max_length=200, verbose_name="Название (тадж.)")
    title_rus = models.CharField(max_length=200, verbose_name="Название (рус.)")
    title_eng = models.CharField(max_length=200, verbose_name="Название (англ.)")
    title_kor = models.CharField(max_length=200, verbose_name="Название (кор.)")

    # Описания на 4 языках
    description_taj = models.TextField(verbose_name="Описание (тадж.)")
    description_rus = models.TextField(verbose_name="Описание (рус.)")
    description_eng = models.TextField(verbose_name="Описание (англ.)")
    description_kor = models.TextField(verbose_name="Описание (кор.)")

    author = models.CharField(max_length=255, verbose_name="Автор")
    genres = models.CharField(max_length=30, choices=GENRES_CHOICES, blank=True, verbose_name="Жанр")
    published_date = models.DateField(blank=True, null=True, verbose_name="Дата публикации")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Добавлено")

    # Файлы хранятся на Google Drive
    cover = models.ImageField(
        upload_to="Sejong Cloud/book/covers",
        storage=gd_storage,
        blank=True, null=True,
        verbose_name="Обложка"
    )
    file = models.FileField(
        upload_to="Sejong Cloud/book/files",
        storage=gd_storage,
        verbose_name="Файл книги"
    )

    # Кешированные прямые ссылки — заполняются автоматически в save()
    # Не редактировать вручную (readonly в Admin)
    cover_id = models.CharField(max_length=250, blank=True, null=True)
    file_id  = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'elibrary'
        ordering = ['-created_at']
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.title_eng or self.title_rus

    def save(self, *args, **kwargs):
        """
        Сохраняем объект ОДИН раз.
        Перед записью вычисляем cover_id / file_id из URL Google Drive,
        чтобы не делать второй super().save() после основного.
        """
        # Вычисляем ссылки ДО сохранения, если файл уже загружен
        if self.cover and self.cover.name:
            try:
                url = self.cover.storage.url(self.cover.name)
                self.cover_id = extract_drive_id(url, download=False)
            except Exception:
                pass  # Файл ещё не загружен на Drive — ничего страшного

        if self.file and self.file.name:
            try:
                url = self.file.storage.url(self.file.name)
                self.file_id = extract_drive_id(url, download=True)
            except Exception:
                pass

        super().save(*args, **kwargs)
