from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('groups/', views.get_user_groups, name='get_user_groups'),
    path('login/', views.login_view, name='login_view'),
    path('change_username/', views.change_username, name='change_username'),
    path('change_password/', views.change_password, name='change_password'),
]
