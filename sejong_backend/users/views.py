from django.http import JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.authtoken.models import Token


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
    if request.method == "POST":
        # Проверяем токен
        user = check_token(request)
        if isinstance(user, JsonResponse):
            return user  # Возвращаем ошибку, если токен неверный
        
        else:
            try:
                data = json.loads(request.body.decode("UTF-8"))
                new_avatar = data.get("new_avatar")

                if not new_avatar:
                    return JsonResponse({"message": "Avatar is required"}, status=400)
                
                user.avatar = new_avatar
                user.save()
            
            except Exception as e:
                return JsonResponse({"ERROR": str(e)})
        
    return JsonResponse({"error": "Only POST requests are allowed"})                



@csrf_exempt
def change_info(request):
    if request.method == "POST":
        user = check_token(request)
        
        if isinstance(user, User):
            try:
                auth_token = request.headers.get("token")
                data = json.loads(request.body.decode("UTF-8"))
                username = data.get("username")
                check_password = data.get("check_password")
                password = data.get("password")
                phone_number = data.get("phone_number")
                email = data.get("email")
                # avatar = data.get("avatar")
                
                if username:
                    if User.objects.filter(username=username).exists(): #Если существует такой же никнейм
                        return JsonResponse(
                            {"message": "This username is already taken. Please choose another username"},
                            status=400
                        )
                    else:
                        user.username = username
                        return JsonResponse({"username": user.username})
                       
                
                if user.check_password(check_password):  # проверяем текущий пароль
                    if password:  # если есть новый пароль
                        user.set_password(password)  # Django сам захэширует
                        return JsonResponse({"password": user.password})
                else:
                    return JsonResponse(
                        {"message": "Password incorrect, please write the correct current password"},
                        status=400
                    )
                
                if phone_number:
                    user.phone_number = phone_number
                    return JsonResponse({"phone_number": user.phone_number})
                
                if email:
                    user.email = email
                    return JsonResponse({"email": user.email})
                
                # if avatar:
                #     change_avatar(avatar)

                user.save()
                return JsonResponse({
                    "message": "Success",
                    "auth_token": auth_token,
                    "user_data": {
                        "username": user.username,
                        "fullname": user.fullname,
                        "phone_number": user.phone_number,
                        "email": user.email,
                    },
                })
            
            except Exception as e:
                return JsonResponse({"ERROR": str(e)})
        else:
            return user



# @csrf_exempt
# def login_view(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body.decode("utf-8"))  # Декодируем и парсим JSON
#             username = data['username'] if 'username' in data else None
#             password = data['password'] if 'password' in data else None
#             if (not username) or (not password):
#                 return JsonResponse({'error': 'Please send correct data'})

#             user = authenticate(request, username = username, password = password)
#             if user:
#                 token = Token.objects.get(user=user)
#                 return JsonResponse({"token": token.key})
                
#             else:
#                 return JsonResponse({"error": "user not found"}) 
#         except Exception as e:
#             return JsonResponse({"ERROR": str(e)})
#     return JsonResponse({"message": "Only POST requests are allowed"})




# @csrf_exempt
# def change_info(request):
#     if request.method == "POST":
#         token = check_token(request)
#         if token:
#             try:
#                 data = json.loads(request.body.decode("UTF-8"))
#                 username = data.get("username")
#                 password = data.get("password")
#                 # phone_number = data.get("phone_number")
#                 email = data.get("email")
#                 # avatar = data.get("avatar")
                
#                 if username:
#                     token.username = username
                
#                 if password:
#                     token.set_password(password)
                
#                 # if phone_number:
#                 #     token.phone_number = phone_number
                
#                 if email:
#                     token.email = email
                
#                 # if avatar:
#                 #     change_avatar(avatar)

#                 token.save()
#                 return JsonResponse({ "message": f"Success, data: {token}", "auth_token": token })
            
#             except Exception as e:
#                 return JsonResponse({"ERROR": str(e)})




# def get_user_groups(request):
#     if request.method == "GET":
#         token = check_token(request)

#         if token:
#             return JsonResponse({
#                 'groups': token.get_groups(),
#             })


# @csrf_exempt
# def change_username(request):
#     if request.method == "POST":
#         token = check_token(request)
#         if token:
#             try:
#                 data = json.loads(request.body.decode("utf-8"))
#                 new_username = data.get("new_username")
#                 if not new_username:
#                     return JsonResponse({"error": "Username is required"}, status=400)
                
#                 if User.objects.filter(username = new_username).exists():
#                     return JsonResponse({"error": "Username already taken"})
                
#                 token.username = new_username
#                 token.save()
#                 return JsonResponse({"message": "Username updated successfully", "new_username": new_username})

#             except Exception as e:
#                 return JsonResponse({"ERROR": str(e)})
            
#     return JsonResponse({"error": "Only POST requests are allowed"})

# @csrf_exempt
# def change_password(request):
#     if request.method == "POST":
#         token = check_token(request)
#         if token:
#             try:
#                 data = json.loads(request.body.decode("utf-8"))
#                 new_password = data.get("new_password")

#                 if not new_password:
#                     return JsonResponse({"error": "Password is required"}, status=400)
                
#                 token.set_password(new_password)
#                 token.save()
#                 return JsonResponse({"message": "Password updated successfully", "new_password": new_password})

#             except Exception as e:
#                 return JsonResponse({"ERROR": str(e)})
        
#     return JsonResponse({"error": "Only POST requests are allowed"})


# @csrf_exempt
# def change_number(request):
#     if request.method == "POST":
#         token = check_token(request)
#         if token:
#             try:
#                 data = json.loads(request.body.decode("UTF-8"))
#                 new_number = data.get("new_number")

#                 if not new_number:
#                     return JsonResponse({"message": "PhoneNumber is required"}, status=400)
                
#                 token.phone_number = new_number
#                 token.save()
#                 return JsonResponse({"message": "Data updated successfully"})

#             except Exception as e:
#                 return JsonResponse({"ERROR": str(e)})

#     return JsonResponse({"error": "Only POST requests are allowed."})