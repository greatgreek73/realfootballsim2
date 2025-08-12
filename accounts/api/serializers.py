from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    has_club = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "tokens", "money", "is_staff", "has_club")

    def get_has_club(self, obj):
        return hasattr(obj, "club")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, required=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")

    def validate_email(self, value):
        # Уникальный и обязательный email
        if not value:
            raise serializers.ValidationError("Email обязателен.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.pop("password2", None)
        if password != password2:
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        # Валидация пароля стандартными валидаторами Django
        validate_password(password)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
