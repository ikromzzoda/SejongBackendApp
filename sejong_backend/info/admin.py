from django.contrib import admin
from .models import Schedule, TimeSlot, Announcement, AnnouncementImage, Notice, GeminiChat, GeminiMessage


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'classroom')
    list_filter = ('day', 'classroom')
    ordering = ('day', 'start_time')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    readonly_fields = ('time',)
    list_display = ('group_name', 'teacher', 'book')
    list_filter = ('teacher', 'book')
    search_fields = ('teacher',)
    ordering = ('teacher',)


@admin.register(AnnouncementImage)
class AnnouncementImageAdmin(admin.ModelAdmin):
    readonly_fields = ('google_drive_file_id',)
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    readonly_fields = ('custom_id', 'images', 'time_posted')
    list_display = ('title_eng', 'author', 'is_active', 'time_posted')
    list_filter = ('is_active', 'time_posted')
    search_fields = ('title_eng', 'title_rus', 'author')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    readonly_fields = ('image_url',)
    list_display = ('title_eng', 'version_number')
    search_fields = ('title_eng', 'title_rus')
    ordering = ('-version_number',)


# ─── Gemini ───────────────────────────────────────────────────────────────────

class GeminiMessageInline(admin.TabularInline):
    model = GeminiMessage
    readonly_fields = ('question', 'answer', 'time')
    extra = 0
    can_delete = False
    ordering = ('time',)


@admin.register(GeminiChat)
class GeminiChatAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'title', 'user', 'created_at', 'message_count')
    search_fields = ('chat_id', 'title', 'user__username')
    readonly_fields = ('chat_id', 'user', 'created_at')
    ordering = ('-created_at',)
    inlines = [GeminiMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Сообщений'


@admin.register(GeminiMessage)
class GeminiMessageAdmin(admin.ModelAdmin):
    list_display = ('short_question', 'chat', 'time')
    search_fields = ('question', 'chat__chat_id', 'chat__user__username')
    readonly_fields = ('chat', 'question', 'answer', 'time')
    ordering = ('-time',)

    def short_question(self, obj):
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question
    short_question.short_description = 'Вопрос'
