from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения профиля — GET /api/profile/"""
    groups = serializers.SerializerMethodField()
    avatar = serializers.CharField(source='avatar_id')

    class Meta:
        model = User
        fields = ['username', 'fullname', 'email', 'status', 'avatar', 'groups']

    def get_groups(self, obj):
        return obj.get_groups()


class ChangeInfoSerializer(serializers.Serializer):
    """Сериализатор для изменения данных профиля — POST /api/change_info/"""
    username     = serializers.CharField(required=False)
    email        = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    check_password = serializers.CharField(required=False, write_only=True)
    password       = serializers.CharField(required=False, write_only=True)

    def validate_phone_number(self, value):
        validator = RegexValidator(
            regex=r'^\+992\d{9}$',
            message="Номер должен начинаться с '+992' и содержать 9 цифр после него."
        )
        validator(value)
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Это имя пользователя уже занято.")
        return value
