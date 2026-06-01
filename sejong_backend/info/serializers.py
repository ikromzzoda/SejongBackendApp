from rest_framework import serializers
from .models import Schedule, Announcement, Notice, GeminiChat, GeminiMessage


class ScheduleSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['group', 'teacher', 'book', 'time']

    def get_group(self, obj):
        first = obj.group.first()
        return first.name if first else None


class AnnouncementSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['custom_id', 'title', 'content', 'images', 'time_posted', 'author', 'is_active']

    def get_title(self, obj):
        return {'taj': obj.title_taj, 'rus': obj.title_rus,
                'eng': obj.title_eng, 'kor': obj.title_kor}

    def get_content(self, obj):
        return {'taj': obj.content_taj, 'rus': obj.content_rus,
                'eng': obj.content_eng, 'kor': obj.content_kor}


class NoticeSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = ['title', 'content', 'images', 'version_number']

    def get_title(self, obj):
        return {'taj': obj.title_taj, 'rus': obj.title_rus,
                'eng': obj.title_eng, 'kor': obj.title_kor}

    def get_content(self, obj):
        return {'taj': obj.content_taj, 'rus': obj.content_rus,
                'eng': obj.content_eng, 'kor': obj.content_kor}

    def get_images(self, obj):
        return obj.image_url or []


class GeminiMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeminiMessage
        fields = ['question', 'answer']


class GeminiChatSerializer(serializers.ModelSerializer):
    messages = GeminiMessageSerializer(many=True, read_only=True)

    class Meta:
        model = GeminiChat
        fields = ['chat_id', 'title', 'created_at', 'messages']
