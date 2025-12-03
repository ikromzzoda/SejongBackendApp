from django.urls import path
from . import views

urlpatterns = [
    path('schedules/', views.get_schedules, name='get_schedules'),
    path('announcements/', views.get_all_announcements, name='get_all_announcements'),
    path('notice/', views.get_notices, name='get_notices'),
]