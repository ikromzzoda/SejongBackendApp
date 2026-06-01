from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Groups
from .forms import UserAdminForm

admin.site.site_header = "Sejong Administration"
admin.site.index_title = "King Sejong Institute Dushanbe 3"
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminForm
    model = User
    readonly_fields = ('avatar_id', 'date_joined')

    list_display = ('username', 'fullname', 'email', 'phone_number', 'status', 'date_joined', 'is_active')
    list_filter = ('status', 'group', 'date_joined', 'is_active')
    search_fields = ('username', 'fullname', 'email', 'phone_number')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Личные данные', {
            'fields': ('fullname', 'email', 'phone_number', 'date_of_birth', 'status', 'group', 'avatar', 'avatar_id')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'fullname', 'email', 'phone_number',
                'date_of_birth', 'status', 'group', 'avatar',
                'password1', 'password2',
                'is_active', 'is_staff', 'is_superuser',
            ),
        }),
    )


@admin.register(Groups)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'user_count')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('participant_names_admin', 'created_at')

    fieldsets = (
        ('Информация о группе', {
            'fields': ('name', 'participant_names_admin')
        }),
    )
