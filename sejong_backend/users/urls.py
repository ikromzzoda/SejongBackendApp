from django.urls import path, include, re_path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('profile/', views.get_profile_info, name='get_profile_info'),  
    path('change_info/', views.change_info, name='change_info'),  
    path('change_avatar/', views.change_avatar, name='change_avatar'),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
