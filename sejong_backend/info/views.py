from django.http import JsonResponse
from .models import Schedule, Announcement, Notice
from rest_framework.authtoken.models import Token
from .models import GeminiChat, GeminiMessage
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

    """"
    POST /gemini/save/

    Тело запроса (JSON):
    {
        "chat_id":  "уникальный-id-чата-с-фронта",
        "title":    "Название чата",
        "question": "Вопрос пользователя",
        "answer":   "Ответ Gemini"
    }

    Логика:
    - Если чат с таким chat_id уже существует → добавляем новое сообщение (question/answer)
    - Если чата нет → создаём чат, затем добавляем первое сообщение
    Таким образом один chat_id может содержать много пар question/answer. 
    """
    
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
    chat_id  = body.get("chat_id",  "").strip()
    title    = body.get("title",    "").strip()
    question = body.get("question", "").strip()
    answer   = body.get("answer",   "").strip()

    # Валидация
    if not chat_id:
        return JsonResponse({"error": "Поле 'chat_id' обязательно"}, status=400)
    if not title:
        return JsonResponse({"error": "Поле 'title' обязательно"}, status=400)
    if not question:
        return JsonResponse({"error": "Поле 'question' обязательно"}, status=400)
    if not answer:
        return JsonResponse({"error": "Поле 'answer' обязательно"}, status=400)
  
    # Получаем или создаём чат
    chat, created = GeminiChat.objects.get_or_create(
        chat_id=chat_id,
        defaults={
            "user": user,
            "title": title
        }
    )

    # защита — чужой chat_id
    if chat.user != user:
        return JsonResponse({"error": "Нет доступа к этому чату"}, status=403)

    # Обновление title (если фронт поменял)
    if chat.title != title:
        chat.title = title
        chat.save(update_fields=["title"])
    
    # Добавляем новое сообщение в этот чат
    # Один chat_id → много GeminiMessage (question + answer)
    message = GeminiMessage.objects.create(
        chat=chat,
        question=question,
        answer=answer,
    )

    return JsonResponse({
        "success": True,
        "chat_created": created,           # True если чат был создан, False если уже существовал
        #"message_id": str(message.pk),     # id сохранённого сообщения
        #"chat_id": chat.chat_id,
        "title": chat.title,
    }, status=201)


@csrf_exempt
def get_gemini_history(request):
    """
    GET /gemini/history/

    Возвращает все чаты пользователя вместе со всеми сообщениями.
    Структура ответа:
    [
        {
            "chat_id": "...",
            "title":   "...",
            "created_at": "...",
            "messages": [
                {"question": "...", "answer": "...", "time": "..."},
                ...  // все пары question/answer этого чата
            ]
        },
        ...
    ]
    """

    if request.method != "GET":
        return JsonResponse({"error": "Только GET запросы"}, status=405)

    user = check_token(request)
    if isinstance(user, JsonResponse):
        return user

    # prefetch_related — одним запросом подтягиваем все сообщения для каждого чата
    chats = GeminiChat.objects.filter(user=user).prefetch_related('messages').order_by('-created_at')

    data = []
    for chat in chats:
        messages_data = [
            {
                "question": msg.question,
                "answer":   msg.answer,
                #"time":     msg.time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for msg in chat.messages.all()   # уже отсортированы по time (Meta: ordering = ['time'])
        ]

        data.append({
            "chat_id":    chat.chat_id,
            "title":      chat.title,
            "created_at": chat.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "messages":   messages_data,
        })

    return JsonResponse(data, safe=False)
