from django.contrib import admin
from .models import Schedule, TimeSlot, Announcement, AnnouncementImage

# Register Schedule model
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    readonly_fields = ('time',)

    list_display = ('group_name', 'teacher')
    search_fields = ('group_name', 'teacher')
    list_filter = ('group', 'teacher', 'book')
    

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    readonly_fields = ('custom_id', 'images',)

    list_display = ('title', 'author', 'time_posted')
    search_fields = ('title',)
    list_filter = ('title', 'time_posted')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'classroom')  # Customize fields to display in admin
    search_fields = ('day', 'start_time', 'end_time', 'classroom')      # Add search functionality
    list_filter = ('day', 'start_time', 'end_time', 'classroom')        # Add filter options


@admin.register(AnnouncementImage)
class AnnouncementImageAdmin(admin.ModelAdmin):
    readonly_fields = ('google_drive_file_id',)

    list_display = ('image',)
    search_fields = ('image',)  # Add search functionality
    list_filter = ('image',)