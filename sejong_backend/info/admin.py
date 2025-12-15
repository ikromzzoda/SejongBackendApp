from django.contrib import admin
from .models import Schedule, TimeSlot, Announcement, AnnouncementImage, Notice

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    readonly_fields = ('time',)

    list_display = ('group_name', 'teacher')
    search_fields = ('group_name', 'teacher')
    list_filter = ('group', 'teacher', 'book')
    ordering = ('group',)
    

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'classroom') 
    search_fields = ('day', 'start_time', 'end_time', 'classroom')      
    list_filter = ('day', 'start_time', 'end_time', 'classroom')
    ordering = ('day', 'start_time')  


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    readonly_fields = ('custom_id', 'images',)

    list_display = ('title_eng', 'author', 'time_posted')
    search_fields = ('title_eng',)
    list_filter = ('title_eng', 'time_posted')      


@admin.register(AnnouncementImage)
class AnnouncementImageAdmin(admin.ModelAdmin):
    readonly_fields = ('google_drive_file_id',)

    list_display = ('image',)
    search_fields = ('image',) 
    list_filter = ('image',)


@admin.register(Notice)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title_eng',)
    search_fields = ('title_eng',)
    list_filter = ('title_eng',)