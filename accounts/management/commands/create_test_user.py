from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Создает тестового пользователя: username=testuser, password=testpass123, email=test@example.com, tokens=100, money=5000"

    def handle(self, *args, **options):
        User = get_user_model()
        username = "testuser"
        email = "test@example.com"
        defaults = {
            "email": email,
            "tokens": 100,
            "money": 5000,
        }
        user, created = User.objects.get_or_create(username=username, defaults=defaults)
        if created:
            user.set_password("testpass123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Создан пользователь: {username} / testpass123"))
        else:
            # Обновим поля, если пользователь уже существует
            updated = False
            for k, v in defaults.items():
                if getattr(user, k, None) != v:
                    setattr(user, k, v)
                    updated = True
            user.set_password("testpass123")
            updated = True
            user.save()
            self.stdout.write(self.style.WARNING(f"Пользователь уже существовал. Обновлены данные и пароль: {username} / testpass123"))
