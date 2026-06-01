import re
from django.db import models, transaction
from django.dispatch import receiver
from gdstorage.storage import GoogleDriveStorage
from django.db.models.signals import m2m_changed
from users.models import Groups

gd_storage = GoogleDriveStorage()


def extract_drive_url(url: str, download: bool = False) -> str | None:
    """Извлекает Google Drive ID и возвращает прямую ссылку."""
    match = re.search(r'id=([^&]+)', url)
    if not match:
        return None
    file_id = match.group(1)
    if download:
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    return f'https://drive.google.com/uc?id={file_id}'


# ─── Counter ──────────────────────────────────────────────────────────────────

class Counter(models.Model):
    collection_name = models.CharField(max_length=100, unique=True)
    current_id = models.IntegerField(default=0)

    class Meta:
        db_table = 'counters'


@transaction.atomic
def get_next_id(collection_name: str) -> int:
    counter, _ = Counter.objects.get_or_create(collection_name=collection_name)
    counter.current_id += 1
    counter.save(update_fields=['current_id'])
    return counter.current_id


# ─── Schedule ─────────────────────────────────────────────────────────────────

class TimeSlot(models.Model):
    day = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.IntegerField(choices=[
        (301, 301), (303, 303), (306, 306), (307, 307), (308, 308),
    ])

    class Meta:
        ordering = ['day', 'start_time']
        verbose_name = "Временной слот"
        verbose_name_plural = "Временные слоты"

    def __str__(self):
        return f"{self.get_day_display()} {self.start_time}–{self.end_time} (каб. {self.classroom})"


class Schedule(models.Model):
    group = models.ManyToManyField(Groups, blank=False, help_text="Группа")
    time_many_to_many = models.ManyToManyField(TimeSlot, blank=False, help_text="Временные слоты")
    # Кешированный JSON для быстрой отдачи в API — обновляется сигналом
    time = models.JSONField(blank=True, null=True)
    teacher = models.CharField(max_length=100, help_text="Преподаватель")
    book = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 9)],
        help_text="Номер книги (1–8)"
    )

    class Meta:
        db_table = 'schedules'
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"

    def group_name(self):
        return self.group.first()

    def __str__(self):
        group = self.group.first()
        return f"{group} — {self.teacher}" if group else self.teacher


@receiver(m2m_changed, sender=Schedule.time_many_to_many.through)
def update_schedule_time(sender, instance, action, **kwargs):
    """Обновляет кеш-поле time при изменении временных слотов."""
    if action in ['post_add', 'post_remove', 'post_clear']:
        instance.time = [
            {
                "day": slot.day,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "classroom": slot.classroom,
            }
            for slot in instance.time_many_to_many.all()
        ]
        instance.save(update_fields=['time'])


# ─── Announcement ─────────────────────────────────────────────────────────────

class AnnouncementImage(models.Model):
    title = models.CharField(max_length=200, help_text="Заголовок изображения")
    image = models.ImageField(
        upload_to='Sejong Cloud/announcement/images',
        storage=gd_storage,
        blank=True,
    )
    # Кешированная прямая ссылка — заполняется автоматически в save()
    google_drive_file_id = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = "Изображение объявления"
        verbose_name_plural = "Изображения объявлений"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Вычисляем ссылку ДО сохранения — один save() вместо двух
        if self.image and self.image.name:
            try:
                url = self.image.storage.url(self.image.name)
                self.google_drive_file_id = extract_drive_url(url)
            except Exception:
                pass
        super().save(*args, **kwargs)


class Announcement(models.Model):
    custom_id = models.IntegerField(unique=True, blank=True, null=True)

    title_taj = models.CharField(max_length=200, default="", help_text="Заголовок (тадж.)")
    title_rus = models.CharField(max_length=200, default="", help_text="Заголовок (рус.)")
    title_eng = models.CharField(max_length=200, default="", help_text="Заголовок (англ.)")
    title_kor = models.CharField(max_length=200, default="", help_text="Заголовок (кор.)")

    content_taj = models.TextField(default="", help_text="Текст (тадж.)")
    content_rus = models.TextField(default="", help_text="Текст (рус.)")
    content_eng = models.TextField(default="", help_text="Текст (англ.)")
    content_kor = models.TextField(default="", help_text="Текст (кор.)")

    images_many_to_many = models.ManyToManyField(AnnouncementImage, blank=True)
    # Кешированный список URL — обновляется сигналом
    images = models.JSONField(blank=True, null=True)

    time_posted = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-time_posted']
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self):
        return self.title_eng or self.title_rus or self.title_taj

    def save(self, *args, **kwargs):
        if self.custom_id is None:
            self.custom_id = get_next_id('announcements')
        super().save(*args, **kwargs)


@receiver(m2m_changed, sender=Announcement.images_many_to_many.through)
def update_announcement_images(sender, instance, action, **kwargs):
    """Обновляет кеш-поле images при изменении связанных изображений."""
    if action in ['post_add', 'post_remove', 'post_clear']:
        instance.images = [
            img.google_drive_file_id
            for img in instance.images_many_to_many.all()
            if img.google_drive_file_id
        ]
        instance.save(update_fields=['images'])


# ─── Notice ───────────────────────────────────────────────────────────────────

class Notice(models.Model):
    title_taj = models.CharField(max_length=200, default="", help_text="Заголовок (тадж.)")
    title_rus = models.CharField(max_length=200, default="", help_text="Заголовок (рус.)")
    title_eng = models.CharField(max_length=200, default="", help_text="Заголовок (англ.)")
    title_kor = models.CharField(max_length=200, default="", help_text="Заголовок (кор.)")

    content_taj = models.TextField(default="", help_text="Текст (тадж.)")
    content_rus = models.TextField(default="", help_text="Текст (рус.)")
    content_eng = models.TextField(default="", help_text="Текст (англ.)")
    content_kor = models.TextField(default="", help_text="Текст (кор.)")

    images = models.ImageField(
        upload_to='Sejong Cloud/notice/images',
        storage=gd_storage,
        help_text="Изображение"
    )
    # Кешированная прямая ссылка — заполняется автоматически в save()
    image_url = models.JSONField(blank=True, null=True)

    version_number = models.FloatField(help_text="Номер версии")

    class Meta:
        db_table = 'notices'
        ordering = ['-version_number']
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return self.title_eng or self.title_rus or self.title_taj or self.title_kor

    def save(self, *args, **kwargs):
        # Вычисляем ссылку ДО сохранения — один save() вместо двух
        if self.images and self.images.name:
            try:
                url = self.images.storage.url(self.images.name)
                direct = extract_drive_url(url)
                self.image_url = [direct] if direct else None
            except Exception:
                pass
        super().save(*args, **kwargs)


# ─── Gemini ───────────────────────────────────────────────────────────────────

class GeminiChat(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='chats',
    )
    chat_id = models.CharField(max_length=255, unique=True, help_text="ID чата с фронтенда")
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'gemini_chats'
        ordering = ['-created_at']
        verbose_name = "Чат Gemini"
        verbose_name_plural = "Чаты Gemini"

    def __str__(self):
        return f"{self.title or 'Без названия'} ({self.chat_id})"


class GeminiMessage(models.Model):
    chat = models.ForeignKey(
        GeminiChat,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    question = models.TextField(help_text="Вопрос пользователя")
    answer = models.TextField(help_text="Ответ Gemini")
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gemini_messages'
        ordering = ['time']
        verbose_name = "Сообщение Gemini"
        verbose_name_plural = "Сообщения Gemini"

    def __str__(self):
        return f"{self.question[:50]}..."
