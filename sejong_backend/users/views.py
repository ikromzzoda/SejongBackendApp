import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status

from .serializers import UserProfileSerializer, ChangeInfoSerializer


class ProfileView(APIView):
    """
    GET /api/profile/
    Возвращает данные профиля текущего пользователя.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class ChangeAvatarView(APIView):
    """
    POST /api/change_avatar/
    Обновляет аватар пользователя.
    Принимает multipart/form-data с полем new_avatar (файл).
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_avatar = request.FILES.get("new_avatar")
        if not new_avatar:
            return Response({"error": "Файл аватара не передан."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        ext = new_avatar.name.rsplit(".", 1)[-1]
        filename = f"avatar_{uuid.uuid4()}.{ext}"

        user.avatar.save(filename, new_avatar)
        user.save()

        return Response({
            "message": "Аватар успешно обновлён.",
            "avatar": user.avatar_id,
        })


class ChangeInfoView(APIView):
    """
    POST /api/change_info/
    Обновляет данные профиля: username, email, phone_number, password.

    Тело запроса (JSON) — все поля необязательные:
    {
        "username":       "новый_логин",
        "email":          "new@email.com",
        "phone_number":   "+992XXXXXXXXX",
        "check_password": "текущий_пароль",   // обязателен при смене пароля
        "password":       "новый_пароль"
    }
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangeInfoSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = request.user
        updated_fields = []
        response_data = {}

        # Обновляем username
        if 'username' in data:
            user.username = data['username']
            updated_fields.append('username')
            response_data['username'] = user.username

        # Обновляем email
        if 'email' in data:
            user.email = data['email']
            updated_fields.append('email')
            response_data['email'] = user.email

        # Обновляем телефон
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
            updated_fields.append('phone_number')
            response_data['phone_number'] = user.phone_number

        # Смена пароля — требует текущего пароля
        if 'password' in data:
            check_password = data.get('check_password')
            if not check_password:
                return Response(
                    {"error": "Для смены пароля укажите текущий пароль в поле 'check_password'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not user.check_password(check_password):
                return Response(
                    {"error": "Неверный текущий пароль."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(data['password'])
            updated_fields.append('password')

            # После смены пароля выдаём новый токен
            Token.objects.filter(user=user).delete()
            new_token = Token.objects.create(user=user)
            response_data['auth_token'] = new_token.key
            response_data['message'] = "Пароль успешно изменён."

        if not updated_fields:
            return Response({"message": "Нет данных для обновления."}, status=status.HTTP_400_BAD_REQUEST)

        user.save()
        response_data['updated_fields'] = updated_fields
        return Response(response_data)
