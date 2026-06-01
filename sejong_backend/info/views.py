import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Schedule, Announcement, Notice, GeminiChat, GeminiMessage
from .serializers import (
    ScheduleSerializer,
    AnnouncementSerializer,
    NoticeSerializer,
    GeminiChatSerializer,
)


# ─── Schedule ─────────────────────────────────────────────────────────────────

class ScheduleListView(ListAPIView):
    """
    GET /api/schedules/
    Возвращает список всех расписаний.
    Поддерживает фильтрацию: ?teacher=Иванов
    """
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


# ─── Announcement ─────────────────────────────────────────────────────────────

class AnnouncementListView(ListAPIView):
    """
    GET /api/announcements/
    Возвращает активные объявления (is_active=True).
    """
    serializer_class = AnnouncementSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Announcement.objects.filter(is_active=True)


# ─── Notice ───────────────────────────────────────────────────────────────────

class NoticeListView(ListAPIView):
    """
    GET /api/notice/
    Возвращает все уведомления (отсортированы по версии, убывание).
    """
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


# ─── Gemini ───────────────────────────────────────────────────────────────────

class SaveGeminiChatView(APIView):
    """
    POST /api/gemini/save/

    Тело запроса (JSON):
    {
        "chat_id":  "уникальный-id-чата-с-фронта",
        "title":    "Название чата",
        "question": "Вопрос пользователя",
        "answer":   "Ответ Gemini"
    }

    Логика:
    - Если чат с таким chat_id уже существует → добавляем новое сообщение
    - Если чата нет → создаём чат, затем добавляем первое сообщение
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        chat_id  = data.get("chat_id",  "").strip()
        title    = data.get("title",    "").strip()
        question = data.get("question", "").strip()
        answer   = data.get("answer",   "").strip()

        # Валидация
        errors = {}
        if not chat_id:  errors["chat_id"]  = "Обязательное поле."
        if not title:    errors["title"]    = "Обязательное поле."
        if not question: errors["question"] = "Обязательное поле."
        if not answer:   errors["answer"]   = "Обязательное поле."
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Получаем или создаём чат
        chat, created = GeminiChat.objects.get_or_create(
            chat_id=chat_id,
            defaults={"user": request.user, "title": title},
        )

        # Защита от чужого chat_id
        if chat.user != request.user:
            return Response({"error": "Нет доступа к этому чату."}, status=status.HTTP_403_FORBIDDEN)

        # Обновляем title если изменился
        if chat.title != title:
            chat.title = title
            chat.save(update_fields=["title"])

        # Добавляем сообщение
        GeminiMessage.objects.create(chat=chat, question=question, answer=answer)

        return Response(
            {"success": True, "chat_created": created, "title": chat.title},
            status=status.HTTP_201_CREATED,
        )


class GeminiHistoryView(ListAPIView):
    """
    GET /api/gemini/history/
    Возвращает все чаты текущего пользователя со всеми сообщениями.
    """
    serializer_class = GeminiChatSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            GeminiChat.objects
            .filter(user=self.request.user)
            .prefetch_related('messages')
        )
