"""
sejong_backend/authentication.py

Единственное место для настройки аутентификации.
Импортируй TokenAuthentication и IsAuthenticated в views вместо
написания check_token() в каждом файле.

Использование в любом view:
    from rest_framework.authentication import TokenAuthentication
    from rest_framework.permissions import IsAuthenticated

    class MyView(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

    # Текущий пользователь доступен как:
        request.user

Или через декоратор для function-based views:
    from rest_framework.decorators import api_view, authentication_classes, permission_classes

    @api_view(['GET'])
    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def my_view(request):
        user = request.user
        ...

Настройки по умолчанию в settings.py (уже заданы в проекте):
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
    }

Если задать DEFAULT_PERMISSION_CLASSES глобально — authentication_classes
и permission_classes можно вообще не указывать в каждом view.
"""

# Этот файл — документация и точка единого импорта.
# Реальная логика живёт в DRF, нам не нужно ничего писать вручную.

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

__all__ = ['TokenAuthentication', 'IsAuthenticated']
