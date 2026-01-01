from django.urls import path
from . import views
from .views import ask_gemini

urlpatterns = [
    path('schedules/', views.get_schedules, name='get_schedules'),
    path('announcements/', views.get_all_announcements, name='get_all_announcements'),
    path('notice/', views.get_notices, name='get_notices'),
    path('gemini/', ask_gemini, name='ask_gemini'),
]