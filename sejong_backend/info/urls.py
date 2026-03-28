from django.urls import path
from . import views

urlpatterns = [
    path('schedules/', views.get_schedules, name='get_schedules'),
    path('announcements/', views.get_all_announcements, name='get_all_announcements'),
    path('notice/', views.get_notices, name='get_notices'),
    path('gemini/save/', views.save_gemini_chat, name='save_gemini_chat'),
    path('gemini/history/', views.get_gemini_history,  name='get_gemini_history'),
]