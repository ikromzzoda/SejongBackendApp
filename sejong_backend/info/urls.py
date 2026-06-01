from django.urls import path
from .views import (
    ScheduleListView,
    AnnouncementListView,
    NoticeListView,
    SaveGeminiChatView,
    GeminiHistoryView,
)

urlpatterns = [
    path('schedules/',       ScheduleListView.as_view(),    name='schedule-list'),
    path('announcements/',   AnnouncementListView.as_view(), name='announcement-list'),
    path('notice/',          NoticeListView.as_view(),       name='notice-list'),
    path('gemini/save/',     SaveGeminiChatView.as_view(),   name='gemini-save'),
    path('gemini/history/',  GeminiHistoryView.as_view(),    name='gemini-history'),
]
