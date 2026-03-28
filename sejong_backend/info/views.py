from django.http import JsonResponse
from .models import Schedule, Announcement, Notice
from rest_framework.authtoken.models import Token
from .models import GeminiChat
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



@csrf_exempt  # Отключаем CSRF для мобильного приложения
def save_gemini_chat(request):
    
    if request.method != "POST":
        return JsonResponse({"error": "Только POST запросы"}, status=405)

    user = check_token(request)
    if isinstance(user, JsonResponse):
        return user  # Возвращаем ошибку, если токен неверный

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Неверный JSON формат"}, status=400)

    # Проверяем, что обязательные поля есть
    question = body.get("question", "").strip()
    answer   = body.get("answer",   "").strip()

    if not question:
        return JsonResponse({"error": "Поле 'question' обязательно"}, status=400)
    if not answer:
        return JsonResponse({"error": "Поле 'answer' обязательно"}, status=400)
  

    # Сохраняем в базу данных
    chat = GeminiChat.objects.create(
        user=user,
        question=question,
        answer=answer
    )

    # Возвращаем успешный ответ
    return JsonResponse({
        "success": True,
        "message": "Сохранено успешно"
    }, status=201)


@csrf_exempt
def get_gemini_history(request):
    '''
    Возвращает историю вопросов и ответов для текущего пользователя.
    Фронтенд может показывать студенту его историю переводов и вопросов
    '''
    if request.method != "GET":
        return JsonResponse({"error": "Только GET запросы"}, status=405)

    user = check_token(request)
    if isinstance(user, JsonResponse):
        return user

    # Получаем все вопросы этого пользователя (последние 50)
    chats = GeminiChat.objects.filter(user=user).order_by('-time')[:50]

    data = []
    for chat in chats:
        data.append({
            #"id":         str(chat.id),
            "question":   chat.question,
            "answer":     chat.answer,
            "time": chat.time.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse(data, safe=False)
 