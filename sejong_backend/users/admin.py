from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Groups
from .forms import UserAdminForm

admin.site.site_header = "Sejong administration"
admin.site.index_title = "King Sejong Institute Dushanbe 3"
admin.site.unregister(Group)

class UserAdmin(BaseUserAdmin):
    form = UserAdminForm
    model = User
    readonly_fields = ('avatar_id',)

    list_display = ("username", "fullname", "email", "phone_number", "status", "date_joined", "is_active") #group couldn't add, because group is ManytoMany
    list_filter = list_filter = ("status", "group", "date_joined", "is_active")
    search_fields = ('username', 'fullname', 'email', 'phone_number')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('fullname', 'email', 'phone_number', 'date_of_birth', 'status', 'group', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_staff')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'avatar_id')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'fullname', 'email', 'phone_number', 'date_of_birth', 'status', 'group', 'avatar', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

    ordering = ('-date_joined',)
    # exclude = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)


@admin.register(Groups)
class Groups(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'user_count')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('participant_names_admin',)
    
    fieldsets = (
        ('Group info', {
            'fields': ('name', 'participant_names_admin',)}
        ),
    )
    