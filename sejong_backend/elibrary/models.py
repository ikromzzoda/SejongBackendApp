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
    title = models.CharField(max_length=255, verbose_name="Book Title")
    author = models.CharField(max_length=255, verbose_name="Author")
    description = models.TextField(max_length=255, verbose_name="Description", blank=True, null=True)  
    cover = models.ImageField(upload_to="Sejong Cloud/book/covers", verbose_name="Cover", storage=gd_storage, blank=True, null=True) 
    file = models.FileField(upload_to="Sejong Cloud/book/files", storage=gd_storage)  
    genres = models.CharField(max_length=30, choices=GENRES_CHOICES, blank=True)
    published_date = models.DateField(verbose_name="Date of publication", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    cover_id = models.CharField(max_length=250, blank=True, null=True,) #help_text="<strong><span style='font-size: 16px;'>Don't touch!!!</span></strong>"
    file_id = models.CharField(max_length=250, blank=True, null=True,) #help_text="<strong><span style='font-size: 16px;'>Don't touch!!!</span></strong>"

    class Meta:
        db_table = 'elibrary'
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.cover:
            cover_url = self.cover.storage.url(self.cover.name)
            match_cover = re.search(r'id=([^&]+)', cover_url)
            self.cover_id = f'https://drive.google.com/thumbnail?id={match_cover.group(1)}' if match_cover else None
            super().save(update_fields = ['cover_id'])
        
        if self.file:
            file_url = self.file.storage.url(self.file.name)
            match_file = re.search(r'id=([^&]+)', file_url)
            self.file_id = f'https://drive.google.com/thumbnail?id={match_file.group(1)}' if match_file else None    
            super().save(update_fields = ['file_id'])  

    def __str__(self):
        return self.title
