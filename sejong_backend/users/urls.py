from django.urls import path, include
from .views import ProfileView, ChangeAvatarView, ChangeInfoView

urlpatterns = [
    path('profile/',      ProfileView.as_view(),      name='profile'),
    path('change_info/',  ChangeInfoView.as_view(),    name='change-info'),
    path('change_avatar/', ChangeAvatarView.as_view(), name='change-avatar'),
    path('auth/',         include('djoser.urls.authtoken')),
]
