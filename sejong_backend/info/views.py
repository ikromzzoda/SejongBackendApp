from django.http import JsonResponse
from .models import Schedule, Announcement, Notice
from rest_framework.authtoken.models import Token

import json
from django.views.decorators.csrf import csrf_exempt
from google import genai
from django.conf import settings

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


# Инициализация клиента Gemini
client = genai.Client(api_key=settings.GEMINI_API_KEY)

@csrf_exempt
def ask_gemini(request):
    if request.method == "POST":
        user = check_token(request)
        # Если функция вернула JsonResponse (ошибка), просто возвращаем её
        if isinstance(user, JsonResponse):
            return user
    
        try:
            data = json.loads(request.body)
            user_prompt = data.get("prompt", "")

            if not user_prompt:
                return JsonResponse({"error": "Prompt is empty"}, status=400)

            # Инициализируем модель с системной инструкцией
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config={
                    "system_instruction": (
                        "Ты — специализированный помощник по корейскому языку. "
                        "Твоя задача — отвечать ТОЛЬКО на вопросы, связанные с изучением корейского языка, "
                        "грамматикой, лексикой, культурой Кореи или переводами. "
                        "Если пользователь задает вопрос на любую другую тему (математика, программирование, "
                        "общие вопросы и т.д.), ты должен вежливо ответить: "
                        "'Я отвечаю только на вопросы, связанные с корейским языком.'"
                    )
                },
                contents=user_prompt
            )

            return JsonResponse({"reply": response.text})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        


def get_schedules(request):
    if request.method == "GET":
        user = check_token(request)
        # Если функция вернула JsonResponse (ошибка), просто возвращаем её
        if isinstance(user, JsonResponse):
            return user

        # Получаем расписания
        schedules = Schedule.objects.all()
        data = []

        for schedule in schedules:
            data.append({
                'group': schedule.group.first().name if schedule.group.exists() else None,
                'teacher': schedule.teacher,
                'book': schedule.book,
                "time": schedule.time if schedule.time else [],
            })

        return JsonResponse(data, safe=False)



def get_all_announcements(request):
    if request.method == "GET":
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
    
def get_notices(request):
    if request.method == "GET":
        user = check_token(request)
        if isinstance(user, JsonResponse):
            return user  # Возвращаем ошибку, если токен неверный

        # Получаем все объявления
        notices = Notice.objects.all()
        data = []

        for notice in notices:
            data.append({
                "title": {
                    "taj": notice.title_taj,
                    "rus": notice.title_rus,
                    "eng": notice.title_eng,
                    "kor": notice.title_kor
                },
                "content": {
                    "taj": notice.content_taj,
                    "rus": notice.content_rus,
                    "eng": notice.content_eng,
                    "kor": notice.content_kor
                },
                "images": [image for image in notice.image_url],
                "version": notice.version_number
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