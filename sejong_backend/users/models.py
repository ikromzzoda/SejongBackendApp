import re
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.html import format_html
from gdstorage.storage import GoogleDriveStorage

gd_storage = GoogleDriveStorage()

DEFAULT_AVATAR = "https://drive.google.com/uc?id=1FCfMdEvghunhDuKd1PWQqty_ZPZelqim"


def extract_drive_url(url: str) -> str | None:
    """Извлекает Google Drive ID и возвращает прямую ссылку для отображения."""
    match = re.search(r'id=([^&]+)', url)
    if not match:
        return None
    return f'https://drive.google.com/uc?id={match.group(1)}'


# ─── UserManager ──────────────────────────────────────────────────────────────

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        email = extra_fields.get('email')
        if email:
            extra_fields['email'] = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(username, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(username=username)


# ─── Groups ───────────────────────────────────────────────────────────────────

class Groups(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название группы")
    created_at = models.DateTimeField(auto_now_add=True)

    def user_count(self):
        return self.user_set.count()
    user_count.short_description = "Участников"

    def participant_names_admin(self):
        return format_html("<br>".join(user.fullname for user in self.user_set.all()))
    participant_names_admin.short_description = "Участники"

    class Meta:
        db_table = 'groups'
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ['name']

    def __str__(self):
        return self.name


# ─── User ─────────────────────────────────────────────────────────────────────

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    phone_validator = RegexValidator(
        regex=r'^\+992\d{9}$',
        message="Номер должен начинаться с '+992' и содержать 9 цифр после него."
    )

    STATUS_CHOICES = (
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
        ('Admin',   'Admin'),
    )

    username     = models.CharField(max_length=100, unique=True)
    fullname     = models.CharField(max_length=200)
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=13, validators=[phone_validator])
    date_of_birth = models.DateField(blank=True, null=True)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Student')
    group        = models.ManyToManyField(Groups, related_name="user_set", blank=True)

    avatar    = models.ImageField(
        upload_to="Sejong Cloud/users/avatars",
        storage=gd_storage,
        blank=True,
    )
    # Кешированная прямая ссылка — заполняется автоматически в save()
    # Не редактировать вручную (readonly в Admin)
    avatar_id = models.CharField(
        max_length=250, blank=True, null=True,
        default=DEFAULT_AVATAR,
    )

    date_joined = models.DateTimeField(default=timezone.now)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)

    USERNAME_FIELD  = "username"
    REQUIRED_FIELDS = ['email', 'phone_number']

    class Meta:
        db_table = 'users'
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']

    def get_groups(self):
        return [group.name for group in self.group.all()]

    def save(self, *args, **kwargs):
        # Вычисляем avatar_id ДО сохранения — один save() вместо двух
        if self.avatar and self.avatar.name:
            try:
                url = self.avatar.storage.url(self.avatar.name)
                self.avatar_id = extract_drive_url(url) or DEFAULT_AVATAR
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
