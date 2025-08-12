from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

User = get_user_model()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Проверяем что пользователь с таким email существует"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uid = attrs.get('uid')
        token = attrs.get('token')
        new_password1 = attrs.get('new_password1')
        new_password2 = attrs.get('new_password2')

        if new_password1 != new_password2:
            raise serializers.ValidationError("Пароли не совпадают.")

        # Валидация длины пароля
        if len(new_password1) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов.")

        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Неверная ссылка для сброса пароля.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Ссылка для сброса пароля недействительна или устарела.")

        attrs['user'] = user
        return attrs


class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Генерируем токен и uid
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Формируем ссылку для сброса пароля
            # Используем фронтенд URL
            reset_url = f"{request.scheme}://{request.get_host()}/auth/password-new?uid={uid}&token={token}"
            
            # Отправляем email
            subject = 'Сброс пароля - Real Football Sim'
            message = render_to_string('accounts/password_reset_email.txt', {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'Real Football Sim',
            })
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return Response(
                    {"detail": "Инструкции по сбросу пароля отправлены на ваш email."},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                # В dev окружении возвращаем ссылку в ответе для тестирования
                if settings.DEBUG:
                    return Response(
                        {
                            "detail": "Email не настроен. Ссылка для сброса:",
                            "reset_url": reset_url
                        },
                        status=status.HTTP_200_OK
                    )
                return Response(
                    {"detail": "Ошибка при отправке email. Попробуйте позже."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password1']
            
            # Устанавливаем новый пароль
            user.set_password(new_password)
            user.save()
            
            return Response(
                {"detail": "Пароль успешно изменен."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetValidateTokenView(APIView):
    """Проверка валидности токена сброса пароля"""
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        
        if not uid or not token:
            return Response(
                {"valid": False, "detail": "Требуются uid и token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"valid": False, "detail": "Неверная ссылка."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if default_token_generator.check_token(user, token):
            return Response(
                {"valid": True, "username": user.username},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"valid": False, "detail": "Токен недействителен или устарел."},
            status=status.HTTP_400_BAD_REQUEST
        )