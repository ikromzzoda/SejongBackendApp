from django.urls import path, include, re_path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # path('login/', views.login_view, name='login_view'),
    path('profile/', views.get_profile_info, name='get_profile_info'),
    # path('avatar/', views.change_avatar, name='change_avatar'),
    
    
    path('change_info/', views.change_info, name='change_info'),    
    # path('groups/', views.get_user_groups, name='get_user_groups'),
    # path('change_username/', views.change_username, name='change_username'),
    # path('change_password/', views.change_password, name='change_password'),
    # path('number/', views.change_number, name='change_number'),
    
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
