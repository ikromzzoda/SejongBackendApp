from django.http import JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.authtoken.models import Token
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from gdstorage.storage import GoogleDriveStorage
from django.core.files.base import ContentFile
import uuid

gd_storage = GoogleDriveStorage()


def check_token(request):
    auth_token = request.headers.get("token")
    if not auth_token:
        return JsonResponse({"error": "Token not provided"}, status=401)

    try:
        token = Token.objects.get(key=auth_token)
        user = token.user
    except Token.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=401)

    return user


def get_profile_info(request):
    if request.method == "GET":
        # Проверяем токен
        user = check_token(request)
        if isinstance(user, JsonResponse):
            return user  # Возвращаем ошибку, если токен неверный

        else:
            return JsonResponse ({
                "username": user.username,
                "avatar": user.avatar_id,
                "fullname": user.fullname,
                # "number": token.phone_number,
                "email": user.email,
                "status": user.status,
                "groups": user.get_groups(),
        })            


@csrf_exempt
def change_avatar(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    user = check_token(request)
    if isinstance(user, JsonResponse):
        return user  # Ошибка авторизации

    try:
        # Получаем файл из form-data
        new_avatar = request.FILES.get("new_avatar")
        if not new_avatar:
            return JsonResponse({"error": "No avatar file provided"}, status=400)

        # Создаём новое имя для файла
        ext = new_avatar.name.split(".")[-1]
        filename = f"avatar_{uuid.uuid4()}.{ext}"

        # Сохраняем в модель
        user.avatar.save(filename, new_avatar)
        user.save()

        return JsonResponse({
            "message": "Avatar updated successfully",
            "avatar": getattr(user, "avatar_id", None)
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def change_info(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    user = check_token(request)
    if not isinstance(user, User):
        return user  # если токен неверный — возвращаем ошибку из check_token

    phone_validator = RegexValidator(
    regex=r'^\+992\d{9}$',
    message="Phone number must start with '+992' and be followed by exactly 9 digits."
) 

    try:
        data = json.loads(request.body.decode("utf-8"))
        updated_fields = []
        response_data = {}

        username = data.get("username")
        check_password = data.get("check_password")
        new_password = data.get("password")
        phone_number = data.get("phone_number")
        email = data.get("email")

        if username:
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                return JsonResponse(
                    {"message": "This username is already taken. Please choose another one."},
                    status=400
                )
            user.username = username
            updated_fields.append("username")
            response_data["username"] = username

        if check_password:
            if not user.check_password(check_password):
                return JsonResponse(
                    {"message": "Password incorrect, please enter the correct current password."},
                    status=400
                )
            if new_password:
                user.set_password(new_password)
                updated_fields.append("password")
                response_data["message"] = "Password changed successfully"
                 
                 # обновляем токен
                Token.objects.filter(user=user).delete()
                new_token, created = Token.objects.get_or_create(user=user)
                response_data["auth_token"] = new_token.key
          
        if phone_number:
            try:
                phone_validator(phone_number)
                user.phone_number = phone_number
                updated_fields.append("phone_number")
                response_data["phone_number"] = phone_number
            except ValidationError as e:
                return JsonResponse({"message": e.message}, status=400)

        if email:
            user.email = email
            updated_fields.append("email")
            response_data["email"] = email

        if updated_fields:
            user.save()
            response_data["updated_fields"] = updated_fields
            return JsonResponse(response_data, status=200)

        return JsonResponse({"message": "No changes provided."}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


