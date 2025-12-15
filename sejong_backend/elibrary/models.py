from django.db import models
from django.utils import timezone
from gdstorage.storage import GoogleDriveStorage
import re

gd_storage = GoogleDriveStorage()

class Book(models.Model):
    GENRES_CHOICES = [
        ('Книги Sejong', 'Книги Sejong'),
        ('Книги Topik', 'Книги Topik'),
        ('Художественная литература', 'Художественная литература'),
    ]
    title_taj = models.CharField(max_length=200, blank=False, verbose_name="Book title Tajik")
    title_rus = models.CharField(max_length=200, blank=False, verbose_name="Book title Russian")
    title_eng = models.CharField(max_length=200, blank=False, verbose_name="Book title English")
    title_kor = models.CharField(max_length=200, blank=False, verbose_name="Book title Korean")

    description_taj = models.TextField(blank=False, verbose_name="Book description in Tajik")
    description_rus = models.TextField(blank=False, verbose_name="Book description in Russian")
    description_eng = models.TextField(blank=False, verbose_name="Book description in English")
    description_kor = models.TextField(blank=False, verbose_name="Book description in Korean")
    
    author = models.CharField(max_length=255, verbose_name="Author")
    cover = models.ImageField(upload_to="Sejong Cloud/book/covers", verbose_name="Cover", storage=gd_storage, blank=True, null=True) 
    file = models.FileField(upload_to="Sejong Cloud/book/files", storage=gd_storage)  
    genres = models.CharField(max_length=30, choices=GENRES_CHOICES, blank=True)
    published_date = models.DateField(verbose_name="Date of publication", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    cover_id = models.CharField(max_length=250, blank=True, null=True,) 
    file_id = models.CharField(max_length=250, blank=True, null=True,) 

    class Meta:
        db_table = 'elibrary'
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.cover:
            cover_url = self.cover.storage.url(self.cover.name)
            match_cover = re.search(r'id=([^&]+)', cover_url)
            # Прямая ссылка для скачивания
            self.cover_id =f'https://drive.google.com/uc?id={match_cover.group(1)}' if match_cover else None
            super().save(update_fields = ['cover_id'])
        
        if self.file:
            file_url = self.file.storage.url(self.file.name)
            match_file = re.search(r'id=([^&]+)', file_url)
            # Прямая ссылка для скачивания
            self.file_id = f'https://drive.google.com/uc?export=download&id={match_file.group(1)}' if match_file else None
            super().save(update_fields=['file_id']) 

    def __str__(self):
        return self.title_eng
