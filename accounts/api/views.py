from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Логин по username (как в текущем проекте) + опционально по email
    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        # Если передали email — попробуем найти username по нему
        if isinstance(username_or_email, str) and "@" in username_or_email:
            User = get_user_model()
            try:
                user = User.objects.get(email__iexact=username_or_email)
                # Подменяем username для базовой валидации в TokenObtainPairSerializer
                attrs["username"] = user.username
            except User.DoesNotExist:
                # не нашли — пусть базовый валидатор обработает ошибку
                pass

        data = super().validate(attrs)
        # Добавим user payload в ответ
        user_data = UserSerializer(self.user).data
        data["user"] = user_data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshView(TokenRefreshView):
    permission_classes = (permissions.AllowAny,)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Ожидает refresh токен в теле запроса и помещает его в blacklist.
        Также корректно обработает отсутствующий/некорректный токен.
        """
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": _("Refresh token is required.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            # Не раскрываем детали — просто сообщаем, что запрос некорректен
            return Response({"detail": _("Invalid refresh token.")}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
