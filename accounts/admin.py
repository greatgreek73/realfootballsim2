from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'last_login')  # Добавление 'email' в список
    search_fields = ('username', 'email')  # Убедитесь, что поиск по email также включен

admin.site.register(CustomUser, CustomUserAdmin)
