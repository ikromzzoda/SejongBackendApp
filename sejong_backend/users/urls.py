from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('profile/', views.get_profile_info, name='get_profile_info'),
    # path('avatar/', views.change_avatar, name='change_avatar'),
    path('change_info/', views.change_info, name='change_info'),
    # path('groups/', views.get_user_groups, name='get_user_groups'),
    # path('change_username/', views.change_username, name='change_username'),
    # path('change_password/', views.change_password, name='change_password'),
    # path('number/', views.change_number, name='change_number'),
]
