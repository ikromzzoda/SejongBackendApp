from django.http import JsonResponse
from .models import Schedule, Announcement
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

def get_schedules(request):
    if request.method == "GET":
        # 1️⃣ Проверяем токен
        user = check_token(request)
        # Если функция вернула JsonResponse (ошибка), просто возвращаем её
        if isinstance(user, JsonResponse):
            return user

        # 2️⃣ Получаем расписания
        schedules = Schedule.objects.all()
        data = []

        for schedule in schedules:
            data.append({
                'group': schedule.group.first().name if schedule.group.exists() else None,
                'teacher': schedule.teacher,
                'book': schedule.book,
                "time": schedule.time if schedule.time else [],
            })

        # 3️⃣ Возвращаем ответ
        return JsonResponse(data, safe=False)



def get_all_announcements(request):
    if request.method == "GET":
        # Проверяем токен
        user = check_token(request)
        if isinstance(user, JsonResponse):
            return user  # Возвращаем ошибку, если токен неверный

        # 🔹 Получаем все объявления
        announcements = Announcement.objects.all()
        data = []

        for announcement in announcements:
            data.append({
                "title": {
                    "taj": announcement.title_taj,
                    "rus": announcement.title_rus,
                    "eng": announcement.title_eng,
                    "kor": announcement.title_kor
                },
                "content": {
                    "taj": announcement.content_taj,
                    "rus": announcement.content_rus,
                    "eng": announcement.content_eng,
                    "kor": announcement.content_kor
                },
                # Убедись, что поле images сериализуемое (например, list или str)
                "images": announcement.images,
                "time_posted": announcement.time_posted.strftime("%Y-%m-%d %H:%M:%S"),
                "author": announcement.author,
                "is_active": announcement.is_active,
                "custom_id": announcement.custom_id,
            })

        return JsonResponse(data, safe=False)



# def get_all_announcements(request):
#     if request.method == "GET":
#         # token = check_token(request)
#         # if token:
#         # Assuming you have a model named AnnouncementImage with a field 'image'
#         announcements = Announcement.objects.all()
#         data = []

#         for announcement in announcements:
#             data.append({
#                 "title": {
#                     "taj": announcement.title_taj,
#                     "rus": announcement.title_rus,
#                     "eng": announcement.title_eng,
#                     "kor": announcement.title_kor
#                 },
#                 "content": {
#                     "taj": announcement.content_taj,
#                     "rus": announcement.content_rus,
#                     "eng": announcement.content_eng,
#                     "kor": announcement.content_kor
#                 },
#                 "images": announcement.images,
#                 "time_posted": announcement.time_posted.strftime("%Y-%m-%d %H:%M:%S"),
#                 "author": announcement.author,
#                 "is_active": announcement.is_active,
#                 "custom_id": announcement.custom_id,
#             })
            
#         return JsonResponse(data, safe=False)